# RACTF Code Ingest Server
# Copyright (C) 2019-2020  RACTF Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# import asyncio
import logging
import secrets
import tarfile
import threading
from base64 import b64encode
from binascii import Error
from io import BytesIO
from typing import Dict

import docker


class DockerPipeline():

    def __init__(self, **container_config):

        self.container_config = container_config
        self.docker_client = docker.from_env()

        # This is temporary until a persistent solution is implemented.
        self.result_dict = {}

    async def pull_image(self, img_name) -> None:
        try:
            self.docker_client.images.get(img_name)
            logging.info("Image found, skipping pull.")
        except(docker.errors.ImageNotFound):
            logging.info("Image not found or image changed, will pull now.")
            self.docker_client.images.pull(
                self.container_config.get("image_name", img_name)
            )

    def cp_bytes(self, src, dst, container_token, bytes_obj=True) -> None:

        # Create our in-memory tarfile
        in_mem_tarfile = BytesIO()
        __in_mem_code = BytesIO(src)
        tar_info = tarfile.TarInfo("script")
        tar_info.size = len(src)
        __tar_manager = tarfile.open(fileobj=in_mem_tarfile, mode="w")
        __tar_manager.addfile(tar_info, __in_mem_code)
        __tar_manager.close()

        # Put the archive in the container with format docker-py wants.
        container_dst = self.docker_client.containers.get(container_token)
        container_dst.put_archive(dst, in_mem_tarfile.getvalue())

    def setup_container(self) -> None:
        ...

    def __spawn_threaded_container(self, exec_code, exec_method, container_token) -> None:

        try:
            current_container = self.docker_client.containers.run(
                self.container_config["image_name"],
                "tail -f /dev/null",
                network_disabled=self.container_config['disable_network'],
                mem_limit=self.container_config['mem_max'],
                memswap_limit=self.container_config['mem_max'],
                detach=True,
                remove=self.container_config['auto_remove'],
                stop_signal="SIGKILL",
                name=container_token
            )
            self.cp_bytes(exec_code, "/home", container_token)
            exec_result = list(current_container.exec_run(
                exec_method,
                workdir="/home/",
            ))[::-1]
            exec_result[0] = exec_result[0][:self.container_config['output_max']]
            self.result_dict[container_token] = exec_result
            logging.info(self.result_dict[container_token])
            current_container.stop()

            '''with NamedTemporaryFile() as temp_codefile:
                with open(temp_codefile.name, 'wb') as _code:
                    _code.write(exec_code)

                current_container = self.docker_client.containers.run(
                    self.container_config["image_name"],
                    exec_method,
                    network_disabled=self.container_config['disable_network'],
                    # remove=self.container_config['auto_remove'],
                    volumes={temp_codefile.name: {'bind': '/home/script', 'mode': 'ro'}},
                    mem_limit=self.container_config['mem_max'],
                    memswap_limit=self.container_config['mem_max'],
                    tty=self.container_config['use_tty'],
                    detach=True,
                    stop_signal="SIGKILL",
                    name=container_token
                )
                status_code = current_container.wait()
                output = current_container.logs()[:self.container_config['output_max']]
                current_container.remove()
                self.result_dict[container_token] = [output, status_code.get('StatusCode')]
                logging.info(self.result_dict[container_token])'''

        except(docker.errors.ContainerError):
            return None

    async def run_container(self, exec_code, exec_method) -> Dict[str, str]:

        container_token = secrets.token_hex()
        threading.Thread(target=self.__spawn_threaded_container,
                         args=(exec_code, exec_method, container_token,)).start()
        logging.info(f"Started container {container_token}")

        return {'token': container_token}

    async def poll_result(self, container_token) -> Dict[str, str]:
        error_json = {"result": "Error: Invalid Token, Please Try Again", "status_code": "1"}

        try:

            result = self.result_dict.get(container_token)

            if result is not None:
                del self.result_dict[container_token]
                return {
                    "result": b64encode(result[0]).decode(),
                    "status_code": str(result[1])
                }

            else:
                return error_json

        except(KeyError, ValueError, Error):
            return error_json

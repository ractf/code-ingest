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
from os import walk
from pathlib import Path
from tempfile import gettempdir, NamedTemporaryFile
from typing import Dict

import docker


class DockerPipeline():

    def __init__(self, **container_config):

        self.container_config = container_config
        self.docker_client = docker.from_env()
        self.result_dict = {}
        self.setup_dir = {}
        self.base_dir = Path(gettempdir()) / "ingest_server"

        if not self.base_dir.exists():
            self.base_dir.mkdir()

    async def pull_image(self, img_name, *tokens) -> None:
        try:
            self.docker_client.images.get(img_name)
            logging.info("Image found, skipping build.")
        except(docker.errors.ImageNotFound):
            logging.info("Image not found or image changed, will build now, please wait.")
            self.docker_client.images.build(
                path=str(Path("./docker-build")),
                tag=f"{self.container_config.get('image_name', img_name)}:latest",
                rm=True
            )
            self.docker_client.images.remove("alpine")
            logging.info("Docker Image built successfully.")

        finally:
            if tokens[0]:
                logging.info(f"Admin token is: {tokens[1]}")
                logging.info(f"TOTP base32 secret is: {tokens[2]}")
                logging.info(f"TOTP URL is: {tokens[3]}")
            else:
                logging.info("CODE_INGEST_SPLASH_TOKENS is set, will not display admin tokens.")

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

    async def _build_map(self) -> None:
        path, dirs, files = next(walk(Path("./setup-code")))

    def __spawn_threaded_container(self, exec_code, exec_method, container_token, ext, setup_code) -> None:

        try:

            with NamedTemporaryFile(dir=str(self.base_dir)) as sf, NamedTemporaryFile(dir=str(self.base_dir)) as cf:
                code_dir = self.setup_dir.get(setup_code, None)

                if code_dir is not None:
                    with open(code_dir, "r") as s_code:
                        sf.write(s_code.read())
                        sf.flush()

                cf.write(exec_code)
                cf.flush()

                current_container = self.docker_client.containers.run(
                    self.container_config["image_name"],
                    exec_method,
                    network_disabled=self.container_config['disable_network'],
                    remove=self.container_config['auto_remove'],
                    volumes={temp_codefile.name: {'bind': '/home/ractf/script', 'mode': 'ro'}},
                    mem_limit=self.container_config['mem_max'],
                    memswap_limit=self.container_config['mem_max'],
                    tty=self.container_config['use_tty'],
                    detach=True,
                    stop_signal="SIGKILL",
                    user="ractf",
                    workdir="/home/ractf",
                    name=container_token
                )

            '''with NamedTemporaryFile(dir=str(self.base_dir)) as temp_codefile:
                with open(temp_codefile.name, 'wb') as _code:
                    _code.write(exec_code)

                current_container = self.docker_client.containers.run(
                    self.container_config["image_name"],
                    exec_method,
                    network_disabled=self.container_config['disable_network'],
                    # remove=self.container_config['auto_remove'],
                    volumes={temp_codefile.name: {'bind': '/home/ractf/script', 'mode': 'ro'}},
                    mem_limit=self.container_config['mem_max'],
                    memswap_limit=self.container_config['mem_max'],
                    tty=self.container_config['use_tty'],
                    detach=True,
                    stop_signal="SIGKILL",
                    user="ractf",
                    workdir="/home/ractf",
                    name=container_token
                )
                status_code = current_container.wait()
                output = current_container.logs()[:self.container_config['output_max']]
                current_container.remove()
                self.result_dict[container_token] = [output, status_code.get('StatusCode')]
                logging.info(self.result_dict[container_token])'''


            """current_container = self.docker_client.containers.run(
                self.container_config["image_name"],
                "tail -f /dev/null",
                network_disabled=self.container_config['disable_network'],
                mem_limit=self.container_config['mem_max'],
                memswap_limit=self.container_config['mem_max'],
                detach=True,
                remove=self.container_config['auto_remove'],
                stop_signal="SIGKILL",
                name=container_token,
                user="ractf"
            )
            self.cp_bytes(exec_code, "/home/ractf", container_token)
            exec_result = list(current_container.exec_run(
                exec_method,
                workdir="/home/ractf",
                user="ractf"
            ))[::-1]
            exec_result[0] = exec_result[0][:self.container_config['output_max']]
            self.result_dict[container_token] = exec_result
            logging.info(self.result_dict[container_token])
            current_container.stop()"""

        except(docker.errors.ContainerError):
            return None

    async def run_container(self, exec_code, exec_method, ext, setup) -> Dict[str, str]:

        container_token = secrets.token_hex()
        threading.Thread(target=self.__spawn_threaded_container,
                         args=(exec_code, exec_method, container_token, ext, setup)).start()
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

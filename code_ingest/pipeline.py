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
# from base64 import b64encode
from os import chdir
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict

import docker


class DockerPipeline():

    def __init__(self, **container_config):

        self.container_config = container_config
        self.docker_client = docker.from_env()

    async def pull_image(self) -> None:
        try:
            self.docker_client.images.get("sh3llcod3/codegolf-box")
            logging.info("Image found, skipping pull.")
        except(docker.errors.ImageNotFound):
            logging.info("Image not found, pulling now.")
            self.docker_client.images.pull(
                self.container_config.get("image_name", "sh3llcod3/codegolf-box")
            )

    async def xfr_file(self, src, dst, container_token) -> None:

        container_dst = self.docker_client.containers.get(container_token)
        srcpath = Path(src).resolve()
        srcpath_tar = srcpath.with_suffix('.tar')
        dstpath = Path(dst)
        prev_path = Path.cwd()
        tar = tarfile.open(srcpath_tar, mode='w')
        try:
            chdir(srcpath.parent)
            tar.add(srcpath.parts[-1])
        finally:
            tar.close()
            chdir(prev_path)

        with open(srcpath_tar, "rb") as srcfile:
            container_dst.put_archive(str(dstpath), srcfile.read())

    def setup_container(self) -> None:
        ...

    def __spawn_threaded_container(self, exec_code, exec_method, container_token) -> None:

        try:

            self.setup_container()

            with NamedTemporaryFile() as temp_codefile:
                with open(temp_codefile.name, 'wb') as _code:
                    _code.write(exec_code)

                current_container = self.docker_client.containers.run(
                    self.container_config["image_name"],
                    exec_method,
                    network_disabled=self.container_config['disable_network'],
                    remove=self.container_config['auto_remove'],
                    volumes={temp_codefile.name: {'bind': '/home/script', 'mode': 'ro'}},
                    mem_limit=self.container_config['mem_max'],
                    memswap_limit=self.container_config['mem_max'],
                    tty=self.container_config['use_tty'],
                    # detach=True,
                    stop_signal="SIGKILL",
                    name=container_token
                )
                logging.info(current_container)

        except(docker.errors.ContainerError):
            return None

    async def run_container(self, exec_code, exec_method) -> Dict[str, str]:

        container_token = secrets.token_hex()
        threading.Thread(target=self.__spawn_threaded_container,
                         args=(exec_code, exec_method, container_token,)).start()
        logging.info(f"Started container {container_token}")

        return {'token': container_token}

    async def poll_result(self) -> Dict[str, str]:
        result = ""
        exec_time = ""
        sloc = ""

        return {
            "result": result,
            "time": exec_time,
            "sloc": sloc
        }

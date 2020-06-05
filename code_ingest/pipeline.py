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
import logging
import secrets
import tarfile
import threading
from base64 import b64encode
from binascii import Error
from io import BytesIO
from os import walk
from pathlib import Path
from tempfile import NamedTemporaryFile, gettempdir
from time import sleep
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
            logging.info("This will only happen once, but may take a few minutes.")
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
        for i in enumerate(files):
            self.setup_dir[str(i[0])] = i[1]

    def __manage_container_timeout(self, container_token) -> None:
        sleep(self.container_config["container_lifetime"])
        container, sf, cf = self.result_dict.get(container_token, [None, None, None])
        try:
            if container is not None:
                container.reload()
                if container.attrs["State"]["Running"]:
                    container.kill()
                container.remove()
                logging.info(f"Removed {container_token} as it timed out.")
                del self.result_dict[container_token]

                if sf.exists():
                    sf.unlink()

                if cf.exists():
                    cf.unlink()

        except(docker.errors.NotFound, docker.errors.APIError):
            pass

        return None

    def __spawn_threaded_container(self, exec_code, exec_method, container_token, ext, setup_code) -> None:

        try:
            sf = NamedTemporaryFile(dir=str(self.base_dir), delete=False)
            cf = NamedTemporaryFile(dir=str(self.base_dir), delete=False)

            code_dir = self.setup_dir.get(setup_code, "0blank.sh")
            with open(str(Path("./setup-code") / code_dir), "r") as s_code:
                sf.write(s_code.read().encode())
                sf.flush()

            cf.write(exec_code)
            cf.flush()

            current_container = self.docker_client.containers.run(
                self.container_config["image_name"],
                exec_method,
                network_disabled=self.container_config['disable_network'],
                network_mode=self.container_config['net'],
                remove=self.container_config['auto_remove'],
                volumes={
                    cf.name: {'bind': f'/home/ractf/{ext}', 'mode': 'ro'},
                    sf.name: {'bind': '/home/ractf/setup.sh', 'mode': 'rw'}
                },
                mem_limit=self.container_config['mem_max'],
                memswap_limit=self.container_config['mem_max'],
                tty=self.container_config['use_tty'],
                detach=True,
                stop_signal="SIGINT",
                user="ractf",
                name=container_token,
                isolation="default"
            )
            self.result_dict[container_token] = [current_container, Path(sf.name), Path(cf.name)]
            current_container.reload()
            return None

        except(docker.errors.ContainerError):
            return None

    async def _prune_container(self, **kwargs) -> Dict[str, str]:
        self.docker_client.containers.prune()
        logging.info("Pruned stopped containers.")
        return {'status': "0"}

    async def _kill_container(self, **kwargs) -> Dict[str, str]:
        token = kwargs.get("container", None)
        try:
            if token is not None:
                container = self.docker_client.containers.get(token)
                container.kill()
                container.remove()
                logging.info(f"Killed container {token}")
                return {'status': "0"}
            else:
                return {'status': "1", "result": "Container not found."}

        except(docker.errors.NotFound):
            logging.info("Container not found, not killing.")
            return {'status': "1", "result": "Container not found."}

    async def _get_container_count(self, **kwargs) -> Dict[str, str]:
        return {"number": str(len(self.result_dict)),
                "real": str(len(self.docker_client.containers.list())),
                "status": "0"}

    async def _get_setup_files(self, **kwargs) -> Dict[str, str]:
        return {"files": str(self.setup_dir), "status": "0"}

    async def _reset_all(self, **kwargs) -> Dict[str, str]:
        cont_list = self.docker_client.containers.list()
        for container in cont_list:
            container.remove(v=True, force=True)
        res = self.result_dict

        try:
            for container in self.result_dict:
                self.result_dict[container][0].remove()
                del self.result_dict[container]
        except(RuntimeError):
            ...

        logging.info(f"Removed {len(cont_list)}/{len(res)} containers")
        path, dirs, files = next(walk(Path(self.base_dir)))
        for file in files:
            c_file = self.base_dir / file
            c_file.unlink()
        logging.info(f"Removed {len(files)} files")
        logging.info("Full reset complete")
        return {"status": "0"}

    async def run_container(self, exec_code, exec_method, ext, setup) -> Dict[str, str]:

        container_token = secrets.token_hex()
        threading.Thread(target=self.__spawn_threaded_container,
                         args=(exec_code, exec_method, container_token, ext, setup)).start()
        threading.Thread(target=self.__manage_container_timeout,
                         args=(container_token,)).start()
        logging.info(f"Started container {container_token}")

        return {'token': container_token}

    async def poll_result(self, container_token) -> Dict[str, str]:
        error_json = {"result": "Error: Invalid Token, Please Try Again", "status_code": "1", "done": "1"}
        timeout_json = {"result": "Error: Your code timed out.", "status_code": "1", "done": "0", "timeout": "0"}

        try:

            container, sf, cf = self.result_dict.get(container_token, [None, None, None])

            if container is not None:
                container.reload()
                log = b64encode(container.logs()).decode()

                if container.attrs["State"]["Running"]:
                    state = 1
                    done = 1

                else:
                    state = container.attrs["State"]["ExitCode"]
                    done = 0
                    container.remove()
                    del self.result_dict[container_token]

                    if sf is not None and sf.exists():
                        sf.unlink()
                    if cf is not None and cf.exists():
                        cf.unlink()

                return {
                    "result": log,
                    "status_code": str(state),
                    "done": str(done),
                }

            else:
                return error_json

        except(KeyError, ValueError, Error):
            return error_json
        except(docker.errors.NotFound, docker.errors.ContainerError, docker.errors.APIError):
            return timeout_json

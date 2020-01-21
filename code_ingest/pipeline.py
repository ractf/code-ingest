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
import secrets
import tempfile
import threading

import docker


class DockerPipeline():

    def __init__(self, **container_config):

        self.container_config = container_config
        self.docker_client = docker.from_env()

    def pull_image(self):
        self.docker_client.pull(self.container_config.get("image_name", "sh3llcod3/codegolf-box"))

    def run_container(self, interpreter):

        if interpreter == "python":
            exec_cmd = "python3 /home/script"
        elif interpreter == "gcc":
            exec_cmd = "gcc -x c /home/script -o program; ./program"
        elif interpreter == "cpp":
            exec_cmd = " g++ -x c++ /home/script -o program; ./program"

        self.containers.run(
            self.container_config["image_name"],
            exec_cmd,
            network_disabled=self.container_config['disable_network'],
            remove=self.container_config['auto_remove'],
            volumes={'/home/elliot/scrap/kek': {'bind': '/home/script', 'mode': 'ro'}},
            tty=self.container_config['use_tty']
        )

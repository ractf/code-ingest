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

import docker


class DockerPipeline():

    def __init__(self, **container_config):

        self.container_config = container_config
        self.docker_client = docker.from_env()

    def pull_image(self):
        self.docker_client.images.pull(self.container_config.get("image_name", "sh3llcod3/codegolf-box"))

    def run_container(self, exec_code, exec_method):
        return "test"

        """self.containers.run(
            self.container_config["image_name"],
            exec_method,
            network_disabled=self.container_config['disable_network'],
            remove=self.container_config['auto_remove'],
            volumes={'/home/elliot/scrap/kek': {'bind': '/home/script', 'mode': 'ro'}},
            tty=self.container_config['use_tty']
        )"""

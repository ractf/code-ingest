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

from base64 import b64decode, b64encode
from binascii import Error
from json.decoder import JSONDecodeError
from os import environ
from typing import List, Union

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute, Route

from .pipeline import DockerPipeline

cmd_map = {
    "python": "python3 /home/script",
    "gcc": "gcc -x c /home/script -o program && ./program",
    "cpp": "g++ -x c++ /home/script -o program && ./program",
    "perl": "perl /home/script",
    "ruby": "ruby /home/script",
    "java": "java /home/script",
    "node": "node /home/script"
}

# Setup ENV Vars with some defaults.
IMAGE_NAME = environ.get("CODE_INGEST_IMAGE", "sh3llcod3/ractf-box")
LOG_MAX = environ.get("CODE_INGEST_MAX_OUTPUT", '1001')

code_pipeline = DockerPipeline(
    image_name=IMAGE_NAME,
    file_method="Volumes",
    auto_remove=True,
    container_lifetime=45,
    disable_network=True,
    mem_max="24m",
    use_tty=True,
    output_max=int(LOG_MAX)

)


async def check_image() -> None:
    await code_pipeline.pull_image(IMAGE_NAME)


async def run_code(request) -> JSONResponse:

    try:
        exec_cmd: Union[str, bool] = cmd_map.get(request.path_params.get('interpreter', False), False)

        if not exec_cmd:
            raise ValueError

        data: Union[str, None, bytes] = b64decode((await request.json()).get('exec', None))
        return JSONResponse(
            await code_pipeline.run_container(data, f"/bin/sh -c '{exec_cmd}'")
        )

    except(Error, TypeError, ValueError, JSONDecodeError):
        return JSONResponse(
            {
                'result': b64encode(
                    b"Error: Invalid/missing required parameters or endpoint."
                ).decode()
            }
        )


async def check_result(request) -> JSONResponse:

    try:

        return JSONResponse(
            await code_pipeline.poll_result(request.path_params.get('token', None))
        )

    except(Error, TypeError, ValueError, JSONDecodeError):
        return JSONResponse(
            {
                'result': b64encode(
                    b"Error: Invalid/missing required parameters or endpoint."
                ).decode()
            }
        )


routes: List[BaseRoute] = [
    Route('/run/{interpreter}', run_code, methods=['POST']),
    Route('/poll/{token}', check_result, methods=['POST']),
]

app = Starlette(debug=False, routes=routes, on_startup=[check_image])

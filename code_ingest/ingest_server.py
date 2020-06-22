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
from secrets import compare_digest, token_hex
from typing import List, Union

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute, Route

from .pipeline import DockerPipeline

ext_map = {
    "python": "script.py",
    "gcc": "script.c",
    "cpp": "script.cpp",
    "perl": "script.pl",
    "ruby": "script.rb",
    "java": "program.java",
    "node": "script.js",
    "nasm": "script.asm"
}

cmd_map = {
    "python": f"python3 {ext_map['python']}",
    "gcc": f"gcc {ext_map['gcc']} -o program && ./program",
    "cpp": f"g++ {ext_map['cpp']} -o program && ./program",
    "perl": f"perl {ext_map['perl']}",
    "ruby": f"ruby {ext_map['ruby']}",
    "java": f"java {ext_map['java']}",
    "node": f"node {ext_map['node']}",
    "nasm": (f"nasm -f elf64 {ext_map['nasm']} && "
             "ld -s -o program script.o && ./program")
}

# Setup ENV Vars with some defaults.
IMAGE_NAME = environ.get("CODE_INGEST_IMAGE", "sh3llcod3/code-ingest")
LOG_MAX = environ.get("CODE_INGEST_MAX_OUTPUT", '1001')
MEMORY_LIMIT = environ.get("CODE_INGEST_RAM_LIMIT", "24m")
ADM_TOKEN = environ.get("CODE_INGEST_ADM_TOKEN", token_hex())
DISPLAY_ADM_TOKENS = bool(int(environ.get("CODE_INGEST_SPLASH_TOKENS", "1")))
CONTAINER_TIMEOUT_VAL = int(environ.get("CODE_INGEST_TIMEOUT", "45"))

code_pipeline = DockerPipeline(
    image_name=IMAGE_NAME,
    file_method="Volumes",
    auto_remove=False,
    container_lifetime=CONTAINER_TIMEOUT_VAL,
    disable_network=True,
    net="none",
    mem_max=MEMORY_LIMIT,
    use_tty=False,
    output_max=int(LOG_MAX),
)


async def check_image() -> None:
    await code_pipeline._build_map()
    await code_pipeline.pull_image(IMAGE_NAME, DISPLAY_ADM_TOKENS, ADM_TOKEN)


async def run_code(request) -> JSONResponse:

    try:
        interpreter = request.path_params.get('interpreter', False)
        exec_cmd: Union[str, bool] = cmd_map.get(interpreter, False)
        ext: str = ext_map.get(interpreter, "")
        data: Union[str, None, bytes] = b64decode((await request.json()).get('exec', None))
        setup_file = (await request.json()).get('chall', '0')

        if not (exec_cmd or ext) or data is None:
            raise ValueError

        return JSONResponse(
            await code_pipeline.run_container(
                data,
                (f"/bin/sh -c 'cd /home/ractf; chmod +x setup.sh && sh ./setup.sh;"
                 f" dd if=/dev/null of=setup.sh &>/dev/null; {exec_cmd}'"),
                ext,
                setup_file
            )
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


async def admin_functions(request) -> JSONResponse:

    try:
        act_map = {
            "prune": code_pipeline._prune_container,
            "setupfiles": code_pipeline._get_setup_files,
            "containercount": code_pipeline._get_container_count,
            "kill": code_pipeline._kill_container,
            "reset": code_pipeline._reset_all
        }
        act = request.path_params.get("action", None)
        params = await request.json()
        token = params.get('token', None)
        container = params.get('container', None)

        if token is not None and compare_digest(token, ADM_TOKEN):
            do_act = act_map.get(act, None)

            if do_act is not None:
                resp = await do_act(cont=container)  # type: ignore
                return JSONResponse(resp)

            else:
                raise ValueError

        else:
            return JSONResponse({
                'result': "AuthError: Invalid or missing auth token.",
                'status': "1"
            })

    except(Error, TypeError, ValueError, JSONDecodeError):
        return JSONResponse({
            'result': "Error: Invalid/missing required parameters or endpoint.",
            'status': "1"
        })

routes: List[BaseRoute] = [
    Route('/run/{interpreter}', run_code, methods=['POST']),
    Route('/poll/{token}', check_result, methods=['GET']),
    Route('/admin/{action}', admin_functions, methods=['POST']),
]

app = Starlette(debug=False, routes=routes, on_startup=[check_image])

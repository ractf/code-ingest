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
from secrets import token_hex
from typing import List, Union

import pyotp

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute, Route

from .pipeline import DockerPipeline

cmd_map = {
    "python": "python3 /home/ractf/script",
    "gcc": "gcc -x c /home/ractf/script -o program && ./program",
    "cpp": "g++ -x c++ /home/ractf/script -o program && ./program",
    "perl": "perl /home/ractf/script",
    "ruby": "ruby /home/ractf/script",
    "java": "java /home/ractf/script",
    "node": "node /home/ractf/script",
    "nasm": "nasm -f elf64 /home/ractf/script && ld -s -o program script.o && ./program"
}

ext_map = {
    "python": ".py",
    "gcc": ".c",
    "cpp": ".cpp",
    "perl": ".pl",
    "ruby": ".rb",
    "java": ".java",
    "node": ".js",
    "nasm": ".asm"
}

# Setup ENV Vars with some defaults.
IMAGE_NAME = environ.get("CODE_INGEST_IMAGE", "sh3llcod3/code-ingest")
LOG_MAX = environ.get("CODE_INGEST_MAX_OUTPUT", '1001')
MEMORY_LIMIT = environ.get("CODE_INGEST_RAM_LIMIT", "24m")
ADM_TOKEN = environ.get("CODE_INGEST_ADM_TOKEN", token_hex())
ADM_INIT_2FA_TOKEN = environ.get("CODE_INGEST_MFA_INIT_TOKEN", pyotp.random_base32())
DISPLAY_ADM_TOKENS = bool(int(environ.get("CODE_INGEST_SPLASH_TOKENS", "1")))
TOTP_VERIFY_PREV = bool(int(environ.get("CODE_INGEST_TOTP_COUNTER_REPLAY", "0")))
SETUP_CODE_DIR = environ.get("CODE_INGEST_SETUP_CODE_DIR", "setup-code")

# Setup 2FA
totp = pyotp.TOTP(ADM_INIT_2FA_TOKEN)
TOTP_SECRET_URL = totp.provisioning_uri("code-ingest@ractf.co.uk", issuer_name="RACTF Code Ingest Server")

code_pipeline = DockerPipeline(
    image_name=IMAGE_NAME,
    file_method="Volumes",
    auto_remove=True,
    container_lifetime=45,
    disable_network=True,
    mem_max=MEMORY_LIMIT,
    use_tty=False,
    output_max=int(LOG_MAX),
)
self._build_map()


async def check_image() -> None:
    await code_pipeline.pull_image(IMAGE_NAME, DISPLAY_ADM_TOKENS,
                                   ADM_TOKEN, ADM_INIT_2FA_TOKEN,
                                   TOTP_SECRET_URL)


async def run_code(request) -> JSONResponse:

    try:
        interpreter = request.path_params.get('interpreter', False)
        exec_cmd: Union[str, bool] = cmd_map.get(interpreter, False)
        ext: str = ext_map.get(interpreter, False)
        setup_file = "#!/bin/sh"
        data: Union[str, None, bytes] = b64decode((await request.json()).get('exec', None))
        setup_file = (await request.json()).get('chall', None)

        if not (exec_cmd or ext) or data is None:
            raise ValueError

        return JSONResponse(
            await code_pipeline.run_container(data, f"/bin/sh -c '{exec_cmd}'", ext, setup_file)
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
        return JSONResponse(
            {
                'result': b64encode(
                    b"Error: Not Implemented."
                ).decode()
            }
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
    Route('/poll/{token}', check_result, methods=['GET']),
    Route('/admin/{action}', admin_functions, methods=['POST']),
]

app = Starlette(debug=False, routes=routes, on_startup=[check_image])

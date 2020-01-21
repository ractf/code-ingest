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

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
from starlette.responses import Response

from .pipeline import DockerPipeline

code_pipeline = DockerPipeline(
    image_name="sh3llcod3/codegolf-box",
    exec_method="Volumes",
    auto_remove=True,
    container_lifetime=45,
    disable_network=True,
    use_tty=True,

)

code_pipeline.pull_image()

async def run_python(request):
    ...

async def run_gcc(request):
    ...

async def run_cpp(request):
    ...


app = Starlette(debug=False, routes=[
    Route('/run/python', run_python),
    Route('/run/gcc', run_gcc),
    Route('/run/cpp', run_cpp)
])

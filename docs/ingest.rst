===============================================================================
                               Ingest Server
===============================================================================

**URL Base For Execution:** :code:`/run`
**URL Base For Result:** :code:`/poll`

The latest docker image used for the ingest server can be found at:

- https://hub.docker.com/repository/docker/sh3llcod3/code-ingest

What endpoints are available heavily depends on the Docker Image used.

I am including them all here. However, the the later ones won't work
if you're using an old Image.

******************************************************************************
                                   POST /<token>
******************************************************************************

**Endpoint:** :code:`/poll/<token>`

Retrieve the STDOUT/STDERR of a container, frontend must POST this endpoint
to view the result of any executed code.

Success data:
The returned JSON will have a `result` parameter with the program output.

Wait data:
The returned JSON will have a `done` parameter with a value of `0`.

******************************************************************************
                                   POST /python
******************************************************************************

Run code with python 3.8.1 and return execution result.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+


******************************************************************************
                                   POST /gcc
******************************************************************************

Compile code with GCC-9.2 and return execution result.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+


******************************************************************************
                                   POST /cpp
******************************************************************************

Compile code with G++-9.2 and return execution result.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /perl
******************************************************************************

Runs code with the Perl Interpreter.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /java
******************************************************************************

Runs java code with OpenJDK11-JRE-headless

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /ruby
******************************************************************************

Runs code with Ruby interpreter

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /node
******************************************************************************

Runs code with nodejs.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /nasm
******************************************************************************

Assembles code with nasm and runs the resulting binary.

The resulting binary will be 64-bit to keep the image size down (by not installing the
ia32-libs). Thus the user can utilise 64-bit registers when writing their assembly.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+

===============================================================================
                               Ingest Server
===============================================================================

**URL Base For Execution:** :code:`/run`
**URL Base For Result:** :code:`/poll`
**URL Base For Administration:** :code:`/admin`

The latest docker image is built and hardened automatically if the image is not found.

If you're deploying this for production use, you'll want to set some environment
variables. Though, if you're in a hurry, defaults are used. Nonetheless, here are
some you may consider setting:

- CODE_INGEST_IMAGE: The docker image name to assign the built image, default is "sh3llcod3/code-ingest"
- CODE_INGEST_MAX_OUTPUT: The max number of output characters permitted, default is '1001'
- CODE_INGEST_RAM_LIMIT: The RAM limit of the container, default is "24m"
- CODE_INGEST_ADM_TOKEN: The admin token to use, default is `secrets.token_hex()`
- CODE_INGEST_SPLASH_TOKENS: Whether to display the admin token on startup. Can be `1`/`0`,
  default is `1` (True)
- CODE_INGEST_TIMEOUT: The maximum runtime per container before it times out.

It is assumed the environment variables supplied will be in the correct format.

******************************************************************************
                                   POST /<action>
******************************************************************************

**Endpoint:** :code:`/admin/<action>`

The actions defined so far are:

- :code:`reset`: When supplied, stop all running containers, clear the dict holding any container objects
  remove all the files inside the temporary volumes directory.

- :code:`kill`: When this is specified along with the `container` field, stop that container and
  remove the dict entry. (requires token)

- :code:`prune`: If there are stray containers lying around that have stopped but not been removed, remove them.
  (requires token)

- :code:`setupfiles`: Get the dictionary map which controls which challenge number matches
  which setup file in the `files` parameter. (requires token)

- :code:`containercount`: Return the number of running containers in the `number` parameter
  and return all containers in the `real` parameter. (requires token)

Success data:
The returned JSON will have a `status` parameter with the value `0`

Fail data:
The `status` parameter will be `1` and there will be a `result` parameter will explain the reason for failure.

+----------------------+--------+---------------------------------------------------------------------------------------+
| Field                | Type   | Description                                                                 | Default |
+----------------------+--------+-----------------------------------------------------------------------------+---------+
| token                | string | The admin token set with :code:`CODE_INGEST_ADM_TOKEN` environment variable | ---     |
| container            | string | With certain endpoints, specify a particular container name to act on       | ---     |
+----------------------+--------+-----------------------------------------------------------------------------+---------+


******************************************************************************
                                   GET /<token>
******************************************************************************

**Endpoint:** :code:`/poll/<token>`

Retrieve the STDOUT/STDERR of a container, frontend must GET this endpoint
to view the result of any executed code.

Success data:
The returned JSON will have a `result` parameter with the program output.

Wait data:
The returned JSON will have a `done` parameter with a value of `1`.
When this parameter is `0` the polling can be stopped, as the execution
should have been completed.

******************************************************************************
                                   POST /python
******************************************************************************

Run code with python 3.8.2 and return execution result.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
| chall                | string | (opt) The setup code that needs to be run before    |
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
| chall                | string | (opt) The setup code that needs to be run before    |
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
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /perl
******************************************************************************

Runs code with the Perl 5 v30.1 Interpreter.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /java
******************************************************************************

Runs java code with OpenJDK 11.0.5.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /ruby
******************************************************************************

Runs code with Ruby 2.6.5p114 interpreter.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /node
******************************************************************************

Runs code with NodeJS v12.15.0.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /nasm
******************************************************************************

Assembles code with NASM 2.14.02 and runs the resulting binary.

The resulting binary will be 64-bit to keep the image size down (by not installing the
ia32-libs). Thus the user can utilise 64-bit registers when writing their assembly.

Success data:
The returned JSON will have a `token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

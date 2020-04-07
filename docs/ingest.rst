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
- CODE_INGEST_MFA_INIT_TOKEN: The 2FA TOTP token secret, default is `pyotp.random_base32()`
- CODE_INGEST_SPLASH_TOKENS: Whether to display the Admin & 2FA token on startup. Can be `1`/`0`,
  default is `1` (True)
- CODE_INGEST_TOTP_COUNTER_REPLAY: When set to `1`, verify that TOTP code was not used before.
- CODE_INGEST_SETUP_CODE_DIR: The directory with the setup code to be mounted. The files in this
  directory need to be named according to the parameter that will be supplied from the frontend,
  i.e. passing the optional `challenge` parameter from the `/run` endpoints means, that file
  will be mounted in the container, the setup code ran and the file removed, then the user code is run.

It is assumed the environment variables supplied will be in the correct format.

******************************************************************************
                                   POST /<action>
******************************************************************************

**Endpoint:** :code:`/admin/<action>`

The actions defined so far are:

- :code:`reset`: When supplied, stop all running containers, and clear the dict holding
  the current running containers

- :code:`clear`: Don't stop any containers, but clear the dict holding the running containers.
  This will render any containers created before useless as the result cannot be polled now.
  Thus, use with care.

- :code:`verify2fa`: Verify the 2fa code with the one specified in `2FA`. (requires token & 2FA)

- :code:`regen2fa`: Reset the 2fa code and replace secret with one provided in the `2FA`
  field or generate a random one.

- :code:`stop`: When this is specified along with the `container` field, stop that container and
  remove the dict entry.

- :code:`stat`: When this endpoint is hit, return the equivalent of running `docker status`.
  (requires token, 2FA)

- :code:`containerstat`: Same as the last endpoint but returns stats for a specific container.
  (requires token, 2FA, container)

Success data:
The returned JSON will have a `status` parameter with the value `0`

+----------------------+--------+---------------------------------------------------------------------------------------+
| Field                | Type   | Description                                                                 | Default |
+----------------------+--------+-----------------------------------------------------------------------------+---------+
| token                | string | The admin token set with :code:`CODE_INGEST_ADM_TOKEN` environment variable | random  |
| 2FA                  | string | The 2FA TOTP admin code                                                     | random  |
| new_totp_secret      | string | If `reset2fa` endpoint is hit, replace old TOTP secret with new one         | ---     |
| container            | string | With certain endpoints, specify a particular container to act on            | ---     |
+----------------------+--------+-----------------------------------------------------------------------------+---------+

Note:
The current 2FA implementation will not attempt to validate against replay-attacks of the same TOTP within a 30-sec period by default.
This can be enabled by setting the env-var `CODE_INGEST_TOTP_COUNTER_REPLAY` to `1`/`0` (True/False).

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

===============================================================================
                               Ingest Server
===============================================================================

**URL Base For Execution:** :code:`/run`

**URL Base For Result:** :code:`/poll`

**URL Base For Administration:** :code:`/admin`

*The latest docker image is built and hardened automatically if the image is not found.*

If you're deploying this for production use, you'll want to set some environment
variables.
Though, if you're in a hurry, defaults are used. Nonetheless, here are some you may consider setting:

* CODE_INGEST_IMAGE: The docker image name to assign the built image, default is :code:`sh3llcod3/code-ingest`
* CODE_INGEST_MAX_OUTPUT: The max number of output characters permitted, default is :code:`1000`
* CODE_INGEST_RAM_LIMIT: The RAM limit of the container, default is :code:`24m`
* CODE_INGEST_ADM_TOKEN: The admin token to use, default is :code:`secrets.token_hex()`
* CODE_INGEST_SPLASH_TOKENS: Whether to display the admin token on startup. Can be :code:`1`/:code:`0`,
  default is :code:`1` (True)
* CODE_INGEST_TIMEOUT: The maximum runtime in seconds per container before it times out, defaut is :code:`45`

It is assumed the environment variables supplied will be in the correct format.

Under the :code:`tests/` directory, you can also find :code:`functionality_check.py` which can be used to test
the server out in a hurry. It's poorly written but allows you to access the features. If you've
installed this using poetry venv and you're in the :code:`poetry shell`, just swap the filename with the :code:`ingest_tests`
command, which should be available to you if poetry has setup your :code:`PATH` correctly.

Run a basic functionality test of all the endpoints:

:code:`./functionality_check.py`

Run a stress test:

:code:`./functionality_check.py -s`

Run a prompt to manually test each endpoint:

:code:`./functionality_check.py -i`

Test any of the admin endpoints:

:code:`./functionality_check.py -a {endpoint} -t {admin token} -c {container name if applicable}`

******************************************************************************
                                   POST /<action>
******************************************************************************

**Endpoint:** :code:`/admin/<action>`

The actions defined so far are:

* :code:`reset`: When supplied, stop all running containers, clear any container objects and
  remove all the files inside the temporary volumes directory.

* :code:`kill`: When this is specified along with the :code:`container` field, stop that container and
  remove the dict entry. (requires token, container)

* :code:`prune`: If there are stray containers lying around that have stopped but not been removed, remove them.
  (requires token)

* :code:`setupfiles`: Get the dictionary map which controls which challenge number matches
  which setup file in the :code:`files` response parameter. (requires token)

* :code:`containercount`: Return the number of running containers in the :code:`number` response parameter
  and return all containers in the `real` parameter. (requires token)

Success data:

The returned JSON will have a :code:`status` parameter with the value :code:`0`

Fail data:

The :code:`status` parameter will be :code:`1` and there will be a :code:`result` parameter will explain the reason for failure.

+----------------------+--------+------------------------------------------------------------------------------+
| Field                | Type   | Description                                                                  |
+----------------------+--------+------------------------------------------------------------------------------+
| token                | string | The admin token set with :code:`CODE_INGEST_ADM_TOKEN` environment variable  |
+----------------------+--------+------------------------------------------------------------------------------+
| container            | string | With certain endpoints, specify a particular container name to act on        |
+----------------------+--------+------------------------------------------------------------------------------+


******************************************************************************
                                   GET /<token>
******************************************************************************

**Endpoint:** :code:`/poll/<token>`

Retrieve the STDOUT/STDERR of a container, frontend must GET this endpoint
to view the result of any executed code.

Success data:

The returned JSON will have a :code:`result` parameter with the program output.

Wait data:

The returned JSON will have a :code:`done` parameter with a value of :code:`1`.
When this parameter is :code:`0` the polling can be stopped, as the execution
should have been completed. Adding a counter to limit number of polls and avoid
infinite polling is also recommended.

******************************************************************************
                                   POST /python
******************************************************************************

Run code with python 3.9.0 and return execution result.

Success data:

The returned JSON will have a :code:`token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+


******************************************************************************
                                   POST /gcc
******************************************************************************

Compile code with GCC and return execution result.

Success data:

The returned JSON will have a :code:`token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+


******************************************************************************
                                   POST /cpp
******************************************************************************

Compile code with G++ and return execution result.

Success data:

The returned JSON will have a :code:`token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /perl
******************************************************************************

Runs code with the Perl 5 Interpreter.

Success data:

The returned JSON will have a :code:`token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /java
******************************************************************************

Runs java code with OpenJDK 11.

**Java programs have to have files and classes named in a certain way!**

The file name will be called :code:`program.java` and hence there needs to be a class
in the submitted code called :code:`Program` with a :code:`main` method. This is essential
or else the code will not run!

Here's an example 'Hello, world!' program for demonstration:

:code:`public class Program {public static void main(String[] args) {System.out.println("Hello, World!");}}`

How this class is generated is up to the backend/frontend user, though I will suggest using a template with
this class for the frontend where this code is automatically inserted when the user selects Java for the
language to use.

Success data:

The returned JSON will have a :code:`token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /ruby
******************************************************************************

Runs code with Ruby interpreter.

Success data:

The returned JSON will have a :code:`token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /node
******************************************************************************

Runs code with NodeJS.

Success data:

The returned JSON will have a :code:`token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

******************************************************************************
                                   POST /nasm
******************************************************************************

Assembles code with NASM and runs the resulting binary.

The resulting binary will be 64-bit to keep the image size down (by not installing the
ia32-libs). Thus the user can utilise 64-bit registers when writing their assembly.

Success data:

The returned JSON will have a :code:`token` parameter with the container token.

+----------------------+--------+-----------------------------------------------------+
| Field                | Type   | Description                                         |
+----------------------+--------+-----------------------------------------------------+
| exec                 | string | The code that needs to be executed encoded in b64   |
+----------------------+--------+-----------------------------------------------------+
| chall                | string | (opt) The setup code that needs to be run before    |
+----------------------+--------+-----------------------------------------------------+

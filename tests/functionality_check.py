#!/usr/bin/env python3
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
import random
import threading
import traceback
from base64 import b64decode
from os import environ
from sys import argv
from time import sleep

import requests

# 'Hello, World!\n' in different languages. Fascinating.
the_codes = {
    "python": "cHJpbnQoIkhlbGxvLCBXb3JsZCEiKQo=",
    "gcc": "I2luY2x1ZGUgPHN0ZGlvLmg+CnZvaWQgbWFpbigpIHsKICAgcHV0cygiSGVsbG8sIFdvcmxkISIpOwp9Cg==",
    "cpp": ("I2luY2x1ZGUgPGlvc3RyZWFtPgppbnQgbWFpbigpIHsKICAgIHN0ZDo6Y291dCA8PCAiSGVsbG8gV29ybGQhX"
            "G4iOwogICAgcmV0dXJuIDA7Cn0K"),
    "perl": "IyEvdXNyL2Jpbi9wZXJsCnVzZSBzdHJpY3Q7CnVzZSB3YXJuaW5nczsKCnByaW50ICJIZWxsbywgV29ybGQhXG4iOwo=",
    "ruby": "cHV0cyAiSGVsbG8gV29ybGQhIgo=",
    "java": ("cHVibGljIGNsYXNzIFByb2dyYW0ge3B1YmxpYyBzdGF0aWMgdm9pZCBtYWluKFN0cmluZ1tdIGFy"
             "Z3MpIHtTeXN0ZW0ub3V0LnByaW50bG4oIkhlbGxvLCBXb3JsZCEiKTt9fQo="),
    "node": "Y29uc29sZS5sb2coIkhlbGxvLCBXb3JsZCEiKTsK",
    "nasm": ("CiAgICAgICAgICBnbG9iYWwgICAgX3N0YXJ0CgogICAgICAgICAgc2VjdGlvbiAgIC50ZXh0Cl9z"
             "dGFydDogICBtb3YgICAgICAgcmF4LCAxCiAgICAgICAgICBtb3YgICAgICAgcmRpLCAxCiAgICAg"
             "ICAgICBtb3YgICAgICAgcnNpLCBtZXNzYWdlCiAgICAgICAgICBtb3YgICAgICAgcmR4LCAxNAog"
             "ICAgICAgICAgc3lzY2FsbAogICAgICAgICAgbW92ICAgICAgIHJheCwgNjAKICAgICAgICAgIHhv"
             "ciAgICAgICByZGksIHJkaQogICAgICAgICAgc3lzY2FsbAoKICAgICAgICAgIHNlY3Rpb24gICAu"
             "ZGF0YQptZXNzYWdlOiAgZGIgICAgICAgICJIZWxsbywgV29ybGQhIiwgMTAK")
}

ingest_host = environ.get("INGEST_SERVER_HOST", "0.0.0.0")  # noqa: S104
ingest_port = int(environ.get("INGEST_SERVER_PORT", "5050"))
TIME_DELAY = 4
STRESS_THREADS_MAX = 200


def _run_code(langs):
    try:
        POLL_TIMEOUT = 200
        token = requests.post(
            f"http://{ingest_host}:{ingest_port}/run/{langs}", json={"exec": the_codes[langs]}
        ).json()["token"]
        result = requests.get(
            f"http://{ingest_host}:{ingest_port}/poll/{token}"
        ).json()
        err_result = ["RXJyb3I6IEludmFsaWQvbWlzc2luZyByZXF1aXJlZCBwYXJhbWV0ZXJzIG9yIGVuZHBvaW50Lg==",
                      'Error: Invalid Token, Please Try Again']
        while result["result"] in err_result and POLL_TIMEOUT > 0:
            POLL_TIMEOUT -= 1
            result = requests.get(
               f"http://{ingest_host}:{ingest_port}/poll/{token}"
            ).json()
            sleep(0.3)

        if result["result"] in err_result:
            return f"Error running {langs}"
        else:
            result = b64decode(result["result"]).decode()
        print(f"{langs} says: {result.rstrip()}\n{'-'*80}")
        sleep(0.2)
        return None

    except Exception:
        traceback.print_exc()


# Sequential test
def sequential_test(the_codes) -> None:
    print(f"{'-'*26}Running slow sequential test{'-'*26}")
    for lang in the_codes:
        _run_code(lang)


# Threaded test
def parallel_test(the_codes) -> None:
    print(f"\n{'-'*29}Running parallel test{'-'*30}")
    threads = []
    for lang in the_codes:
        threads.append(threading.Thread(target=_run_code, args=(lang,)))

    for thread in threads:
        thread.start()
        thread.join()


# 2000-thread stress test
def stress_test(the_codes) -> None:
    print(f"\n{'-'*28}Running {STRESS_THREADS_MAX}-thread test{'-'*28}")
    thread_objects = []
    for _ in range(STRESS_THREADS_MAX):
        thread_objects.append(
            threading.Thread(target=_run_code, args=(random.choice(list(the_codes)),)).start()  # noqa: S311
        )

    for t in thread_objects:
        if t is not None:
            t.start()
            t.join()


def run_tests() -> None:
    sequential_test(the_codes)
    parallel_test(the_codes)
    if len(argv) > 1 and argv[1] == "-s":
        stress_test(the_codes)


if __name__ == "__main__":
    run_tests()

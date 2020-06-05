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
import atexit
import random
import threading
import traceback
from base64 import b64decode, b64encode
from os import environ
from sys import argv, exit
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
STRESS_THREADS_MAX = 50  # rip my Proliant
POLL_DURATION = 1
DONE = 0


def _run_code(langs, code=None, poll=False, chall=None):
    try:
        global DONE
        if code is not None:
            global the_codes
            the_codes = {langs: b64encode(code.encode()).decode()}
        POLL_TIMEOUT = 30
        if chall is not None:
            json = {
                "exec": the_codes[langs],
                "chall": chall,
            }
        else:
            json = {
                "exec": the_codes[langs],
            }
        token = requests.post(
            f"http://{ingest_host}:{ingest_port}/run/{langs}",
            json=json
        ).json()["token"]
        result = requests.get(
            f"http://{ingest_host}:{ingest_port}/poll/{token}"
        ).json()
        err_result = ["RXJyb3I6IEludmFsaWQvbWlzc2luZyByZXF1aXJlZCBwYXJhbWV0ZXJzIG9yIGVuZHBvaW50Lg==",
                      'Error: Invalid Token, Please Try Again']
        while result["done"] != "0" and POLL_TIMEOUT > 0:
            POLL_TIMEOUT -= 1
            result = requests.get(
               f"http://{ingest_host}:{ingest_port}/poll/{token}"
            ).json()
            if poll:
                print("Polling:", result)
            sleep(POLL_DURATION)

        if result["result"] in err_result:
            return f"Error running {langs}"
        else:
            raw = result
            if raw.get("timeout", None) is not None:
                result = "Container Timed Out!"
            else:
                result = b64decode(result["result"]).decode()
        print(raw)
        print(f"{langs} says: {result.rstrip()}\n{'-'*80}")
        DONE += 1
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
    print("Botters: Before you ask, my 20k bogomips machine cannot handle 200 threads.")
    for _ in range(STRESS_THREADS_MAX):
        threading.Thread(target=_run_code, args=(random.choice(list(the_codes)),)).start()  # noqa: S311


def run_tests() -> None:
    if len(argv) > 1 and argv[1] == "-s":
        stress_test(the_codes)
        atexit.register(lambda: print(f"Out of {STRESS_THREADS_MAX} threads, {DONE} completed successfully."))
        exit(0)

    elif len(argv) > 1 and argv[1] == "-i":
        while True:
            try:
                c_int = input("Enter endpoint (e.g. python, gcc, etc) >> ")  # noqa: S322
                c_code = input(f"Enter {c_int} code >> ")  # noqa: S322
                c_chall = input("Enter challenge number, default is 0 >> ")  # noqa: S322
                c_poll = True if input("Display polling? y/n >> ").lower().startswith("y") else False  # noqa: S322
                _run_code(c_int, c_code, c_poll, c_chall)
            except(KeyboardInterrupt, EOFError):
                print()
                exit(0)

    elif len(argv) >= 2 and argv[1] == "-a":
        print(
            "Hit admin endpoints, format: ingest_tests -a {endpoint} -t {token} -c {container name if applicable}"
        )

        if len(argv) >= 4:
            endpoint = argv[2]
            token = argv[4] if argv[3] == "-t" else None

            if token is None:
                print("Missing admin token, this is mandatory.")

            if len(argv) >= 6:
                json = {"token": token, "container": argv[6]}
            else:
                json = {"token": token}

            print(requests.post(f"http://{ingest_host}:{ingest_port}/admin/{endpoint}", json=json).json())
            exit(0)

    sequential_test(the_codes)
    parallel_test(the_codes)


if __name__ == "__main__":
    run_tests()

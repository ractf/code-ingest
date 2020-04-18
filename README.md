# RACTF Code Ingest server

This is the code ingest and execution server for RACTF.

This runs code in a time-limited, offline docker container and returns the results.

It's written to meet a specific set of requirements and work in conjunction with a webapp front end.

## Prerequsites & Setup

- python 3.7 or above with pip
- pyenv installed (optional)
- poetry installed

If you don't have the required python version, install [pyenv](https://github.com/pyenv/pyenv#basic-github-checkout) with basic checkout.
Then install the build dependencies, which is listed on the [wiki](https://github.com/pyenv/pyenv/wiki)

Add the following lines to your `~/.bashrc` file (assuming you haven't done so from the pyenv guide):

```bash
# Pyenv installation

if [[ -z "$VIRTUAL_ENV" ]]; then
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
fi
```

If you have a different shell, follow the pyenv install guide. Pyenv isn't mandatory. If you have `python 3.7` or above,
you should be fine.

Next, install [poetry](https://python-poetry.org/docs/) with their suggested way, as this is necessary for the installation.

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```
**Note**: Poetry requires python2, so make sure you have that installed.

## Installation & Deployment

Clone the repo and change directory into it:

```bash
git clone https://gitlab.com/ractf/code-ingest.git
cd code-ingest

# If you're deploying for production.
poetry install --no-dev
poetry shell

# <Set your environment variables here>
ingest_server

# If you're interested in making changes.
poetry install
poetry shell
python -m code_ingest
```

You should be able to use any virtualenv realistically.

The full documentation of environment variables, endpoints, etc can be found in the [docs](docs/ingest.rst)

## Issues

If you encounter a bug, please create an issue stating with as much possible detail:

- Your set-up
- The bug
- Any steps taken

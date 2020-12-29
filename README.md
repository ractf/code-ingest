# RACTF Code Ingest server

This is the code ingest and execution server for RACTF.

This runs code in a time-limited, offline docker container and returns the results.

It's written to meet a specific set of requirements and work in conjunction with a webapp front end.

## Prerequsites & Setup

- Python 3.9.1 or above with pip
- Pyenv installed (optional)
- Poetry installed
- Linux distro, ideally something Debian/Ubuntu based
- Docker [installed](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04) on host

If you don't have the required python version (3.9.1 as of writing), install [pyenv](https://github.com/pyenv/pyenv#basic-github-checkout) with basic checkout.
Then install the build dependencies, which is listed on the [wiki](https://github.com/pyenv/pyenv/wiki)

Add the following lines to your `~/.bashrc` file (assuming you haven't done so from the pyenv guide):

```bash
# Pyenv installation

if [[ -z "$VIRTUAL_ENV" ]]; then
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
fi
```

If you have a different shell, follow the pyenv install guide. Pyenv isn't mandatory if you have the correct version.

Next, install [poetry](https://python-poetry.org/docs/) with their suggested way, as this is necessary for the installation.

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```
**Note**: Poetry requires `python` so if you don't have `python2` you can soft link `python3`: `sudo ln -sf $(which python3) /usr/local/bin/python`

## Installation & Deployment

Clone the repo and change directory into it:

```bash
git clone https://gitlab.com/ractf/code-ingest.git
cd code-ingest

# If you're deploying for production.
poetry install --no-dev
poetry shell

# <Set your environment variables here>
# Remove the docker image every time you want it to be rebuilt.
docker rmi sh3llcod3/code-ingest # If you've not deployed in a while.
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

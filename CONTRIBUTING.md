# Contribution Guidelines

Start by installing pyenv and poetry.

Then clone the repo and change into the relevant directory.

Create the poetry virtualenv with `poetry install`

Run the virtualenv: `poetry shell`

From there, to deploy this app, just type `ingest_server`

Further documentation can be found in the [docs](docs/ingest.rst)

Feel free to suggest code changes.
All code is formatted and tested to be compliant with `flake8`.
Mypy compliance is also followed, just run `mypy` in the repo.

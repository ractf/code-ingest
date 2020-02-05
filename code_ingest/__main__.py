from os import environ

import uvicorn


def main():

    IFACE = environ.get("INGEST_SERVER_HOST", "0.0.0.0")  # noqa: S104
    PORT = int(environ.get("INGEST_SERVER_PORT", "5050"))

    uvicorn.run("code_ingest.ingest_server:app", host=IFACE, port=PORT, debug=False)


if __name__ == "__main__":
    main()

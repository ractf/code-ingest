import uvicorn

IFACE = "0.0.0.0"  # noqa: S104
PORT = 5050

uvicorn.run("code_ingest.ingest_server:app", host=IFACE, port=PORT, debug=False)

import uvicorn

uvicorn.run("code_ingest.ingest_server:app", host="0.0.0.0", port=5050, debug=False)

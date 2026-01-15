#!/bin/bash
# Start API with PORT fallback
PORT=${PORT:-8000}
uvicorn api.main:app --host 0.0.0.0 --port $PORT

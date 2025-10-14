#!/usr/bin/env bash
# Render start script for backend

echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}


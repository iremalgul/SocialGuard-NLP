#!/usr/bin/env bash
# Render build script for backend

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Initializing database..."
python -c "from database.init_db import init_db; init_db()"

echo "Build completed successfully!"


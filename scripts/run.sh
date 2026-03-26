#!/bin/bash

echo "Starting GenAI Conversation Design service..."

if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "Using Python $(python --version)"
else
    echo "Virtual environment not found. Make sure to run 'make install' first."
    exit 1
fi

echo "Running FastAPI application..."
python -m uvicorn app:app --host 0.0.0.0 --port 8000

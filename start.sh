#!/bin/bash

# Start FastAPI backend
echo "Starting FastAPI..."
uvicorn backend.app:app --host 0.0.0.0 --port 8000 &

# Give backend time to start
sleep 5

# Start Streamlit frontend
echo "Starting Streamlit..."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
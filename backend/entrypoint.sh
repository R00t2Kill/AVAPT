#!/bin/bash

# Start FastAPI backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit dashboard
streamlit run app/streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

@echo off
echo ===================================================
echo Starting Medical Assistant Services...
echo ===================================================

echo [1/2] Starting FastAPI Backend in a new window...
start cmd /k ".\venv\Scripts\activate && cd server && uvicorn main:app --reload --port 8001"

echo [2/2] Starting Streamlit Frontend in a new window...
start cmd /k ".\venv\Scripts\activate && streamlit run client/main.py"

echo Both services have been launched! You can close this particular window.

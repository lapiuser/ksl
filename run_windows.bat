@echo off
setlocal
cd /d %~dp0

echo === Kaliningrad School Leaderboard ===
echo.

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Failed to create the virtual environment.
    echo Make sure Python 3 is installed and available through the py launcher.
    pause
    exit /b 1
  )
)

echo [2/3] Installing/updating dependencies...
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo pip failed. Check your internet/PyPI access and try again.
  pause
  exit /b 1
)

echo [3/3] Starting local server...
echo.
echo Open: http://127.0.0.1:8000

echo Press Ctrl+C to stop the server.
call ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

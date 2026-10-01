@echo off
setlocal
cd /d %~dp0
if not exist ".venv\Scripts\python.exe" (
  call run_windows.bat
  exit /b
)
call ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000

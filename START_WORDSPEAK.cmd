@echo off
cd /d "%~dp0"
if not exist "data\phoneme-env\Scripts\python.exe" (
  echo The local speech environment is missing. See ai-service\DEMO.md for setup.
  pause
  exit /b 1
)
echo Starting WordSpeak at http://127.0.0.1:8013/demo
echo Keep this window open. Ctrl+C stops this local server.
"data\phoneme-env\Scripts\python.exe" -u "ai-service\scripts\serve_demo.py" --replace
pause

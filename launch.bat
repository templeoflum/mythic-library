@echo off
echo Starting ACP Explorer...
echo.
echo Press Ctrl+C to stop the server.
echo.
start http://localhost:8000/tools/explorer.html
python -m http.server 8000

#!/bin/bash
echo "Starting ACP Explorer..."
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

# Open browser (works on macOS, Linux with xdg-open, or WSL)
URL="http://localhost:8000/tools/explorer.html"
if command -v open &> /dev/null; then
    open "$URL"
elif command -v xdg-open &> /dev/null; then
    xdg-open "$URL"
elif command -v wslview &> /dev/null; then
    wslview "$URL"
else
    echo "Open your browser to: $URL"
fi

python3 -m http.server 8000 || python -m http.server 8000

"""Simple HTTP server for the Mythic System Explorer.

Serves the miroglyph/ directory as the web root.
All data files (archetypes, entities, patterns, validation, node profiles,
archetype affinities) live in miroglyph/data/ and are served as static files.

Usage:
    python scripts/serve_miroglyph.py [port]
    Default port: 8080
"""
import http.server
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MIROGLYPH_DIR = PROJECT_ROOT / "miroglyph"


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

    if not MIROGLYPH_DIR.exists():
        print(f"Error: {MIROGLYPH_DIR} not found")
        sys.exit(1)

    print(f"Serving Mythic System Explorer from {MIROGLYPH_DIR}")
    print(f"Open http://localhost:{port}")
    print("Press Ctrl+C to stop\n")

    handler = lambda *args, **kw: http.server.SimpleHTTPRequestHandler(
        *args, directory=str(MIROGLYPH_DIR), **kw
    )
    server = http.server.HTTPServer(("", port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()

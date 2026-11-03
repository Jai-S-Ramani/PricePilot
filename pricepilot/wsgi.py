"""
PricePilot Production WSGI Server Launcher
Provides multi-threaded production HTTP serving via Waitress (Windows/Cross-platform)
or Gunicorn (Linux/Containers), with graceful fallback to Flask development server.
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"[PricePilot WSGI] Launching production server on http://{host}:{port}")

    try:
        from waitress import serve
        print(f"[PricePilot WSGI] Serving with Waitress (Production Multi-threaded WSGI, 8 threads)...")
        serve(app, host=host, port=port, threads=8)
    except ImportError:
        print(f"[PricePilot WSGI] Serving with Flask runner...")
        app.run(host=host, port=port, debug=False)

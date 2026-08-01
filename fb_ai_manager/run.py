"""Chạy: python fb_ai_manager/run.py  (rồi mở http://127.0.0.1:5050)"""
import os
import sys
import webbrowser
from threading import Timer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app  # noqa: E402


def _open_browser():
    webbrowser.open("http://127.0.0.1:5050")


if __name__ == "__main__":
    app = create_app()
    Timer(1.0, _open_browser).start()
    app.run(host="127.0.0.1", port=5050, debug=False)

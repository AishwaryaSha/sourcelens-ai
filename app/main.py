"""Streamlit entrypoint for SourceLens AI.

Streamlit executes this file as a script, so the script directory (`app/`) can
become the first import path instead of the project root. Add the project root
explicitly before importing the application package.
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ui.streamlit_app import render_app


if __name__ == "__main__":
    render_app()

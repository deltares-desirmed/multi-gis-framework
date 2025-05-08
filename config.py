# config.py
import tempfile
from pathlib import Path

# Safe, cross-platform downloads directory
DOWNLOADS_PATH = Path(tempfile.gettempdir()) / "streamlit_downloads"
DOWNLOADS_PATH.mkdir(parents=True, exist_ok=True)

# config.py
import tempfile
from pathlib import Path

# A writable path across all environments
DOWNLOADS_PATH = Path(tempfile.gettempdir()) / "streamlit_downloads"
DOWNLOADS_PATH.mkdir(parents=True, exist_ok=True)

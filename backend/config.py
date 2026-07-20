"""
KNWLDGBox — Centralized Path Configuration

Separates read-only application files from writable user data.
In dev mode (running from source), all paths resolve relative to __file__
so existing behavior is preserved. When installed as a package,
user data is stored under XDG_DATA_HOME (Linux) or %APPDATA% (Windows).
"""

import os
import sys
from pathlib import Path


def _is_installed() -> bool:
    """Detect if we're running from a system-installed location."""
    app_dir = Path(__file__).resolve().parent
    # If running from /opt or /usr or C:\Program Files, we're installed
    installed_prefixes = ["/opt/", "/usr/", "C:\\Program Files"]
    return any(str(app_dir).startswith(p) for p in installed_prefixes)


def get_app_dir() -> Path:
    """Read-only application directory (where the Python code lives)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def get_data_dir() -> Path:
    """
    Writable per-user data directory.
    - Installed mode: ~/.local/share/knwldgbox (Linux) or %APPDATA%/knwldgbox (Windows)
    - Dev mode: same as APP_DIR (backend/) for backward compatibility
    """
    if not _is_installed():
        # Dev mode: keep everything in the backend/ folder as before
        return get_app_dir()

    if os.name == 'nt':  # Windows
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    else:  # Linux / macOS
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))

    data_dir = base / 'knwldgbox'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


# ── Core directories ──────────────────────────────────────────────

APP_DIR  = get_app_dir()
DATA_DIR = get_data_dir()

# ── Mutable paths (user data / runtime artifacts) ────────────────

ENV_FILE      = DATA_DIR / '.env'
SESSION_NAME  = str(DATA_DIR / 'anon')       # Telethon appends .session automatically
ARCHIVES_DIR  = DATA_DIR / 'archives'
DOWNLOADS_DIR = DATA_DIR / 'data' / 'downloads'
GRAPHS_DIR    = DATA_DIR / 'data' / 'graphs'
MAIGRET_DIR   = DATA_DIR / 'data' / 'maigret'
TIKTOK_DIR    = DATA_DIR / 'data' / 'tiktok'

# Ensure all mutable directories exist at import time
for _d in [ARCHIVES_DIR, DOWNLOADS_DIR, GRAPHS_DIR, MAIGRET_DIR, TIKTOK_DIR]:
    _d.mkdir(parents=True, exist_ok=True)


# ── Tool resolution ──────────────────────────────────────────────

# When installed, CLI tools live inside the bundled venv
VENV_BIN = APP_DIR / 'venv' / ('Scripts' if os.name == 'nt' else 'bin')


def tool_path(name: str) -> str:
    """
    Resolve a CLI tool name to its full path inside the bundled venv.
    Falls back to the bare command name (system PATH lookup) in dev mode.
    """
    candidate = VENV_BIN / name
    if candidate.exists():
        return str(candidate)
    return name  # Fallback: rely on system PATH (dev mode / conda / venv activated)

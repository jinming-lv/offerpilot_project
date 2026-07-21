"""Project-level environment loader.

Always loads the root .env from the repository root so backend modules do not
depend on the current working directory.
"""

from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_PATH = _PROJECT_ROOT / ".env"
_LOADED = False


def load_project_env() -> str:
    global _LOADED
    if not _LOADED:
        load_dotenv(_ENV_PATH)
        _LOADED = True
    return str(_ENV_PATH)

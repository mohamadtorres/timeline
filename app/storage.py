import json
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "data.json"

def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_state() -> Dict[str, List[Dict[str, Any]]]:
    _ensure_dir()
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"characters": [], "places": [], "events": []}

def save_state(state: Dict[str, List[Dict[str, Any]]]) -> None:
    _ensure_dir()
    DATA_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

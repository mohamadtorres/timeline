import json
import re
from pathlib import Path
from typing import List, Optional
from app.models import Project

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"
PROJECTS_DIR.mkdir(exist_ok=True, parents=True)

def _safe_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\- ]", "", name)
    return name.replace(" ", "_")[:50] or "project"

def project_folder(name: str) -> Path:
    return PROJECTS_DIR / _safe_name(name)

def list_projects() -> List[str]:
    result = []
    for p in PROJECTS_DIR.iterdir():
        if p.is_dir() and (p / "project.json").exists():
            try:
                meta = json.loads((p / "project.json").read_text(encoding="utf-8"))
                result.append(meta.get("name", p.name))
            except Exception:
                result.append(p.name)
    return sorted(result, key=str.lower)

def create_project(name: str) -> Project:
    pf = project_folder(name)
    pf.mkdir(parents=True, exist_ok=True)
    proj = Project(name=name)
    save_project(proj)
    return proj

def load_project(name: str) -> Optional[Project]:
    pf = project_folder(name)
    f = pf / "project.json"
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        return Project.from_dict(data)
    except Exception:
        return None

def save_project(project: Project) -> None:
    pf = project_folder(project.name)
    pf.mkdir(parents=True, exist_ok=True)
    (pf / "project.json").write_text(
        json.dumps(project.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

def delete_project(name: str) -> None:
    pf = project_folder(name)
    f = pf / "project.json"
    if f.exists():
        f.unlink()

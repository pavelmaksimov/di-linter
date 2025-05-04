from pathlib import Path
from typing import Optional, Dict, Any
import tomllib

marker_files = {"setup.py", "setup.cfg", "pyproject.toml", "requirements.txt"}


def validate_path(path: Path):
    if not (path / "__init__.py").exists():
        raise ValueError(f"Path '{path}' does not contain a valid Python package")


def find_project_root(path: Path) -> Path:
    while 1:
        for marker in marker_files:
            if (path.parent / marker).exists():
                return path

        if not (path.parent / "__init__.py").exists():
            return path

        path = path.parent


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    if config_path is None:
        config_path = Path.cwd() / "di.toml"

        if not config_path.exists():
            project_root = find_project_root(config_path)
            config_path = project_root.parent / "di.toml"

    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")

    return {}

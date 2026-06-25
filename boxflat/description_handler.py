import yaml
from pathlib import Path
from typing import Optional


class DescriptionHandler:
    def __init__(self, data_path: str):
        self._descriptions: dict = {}
        self._load(Path(data_path) / "descriptions.yml")

    def _load(self, path: Path) -> None:
        if not path.exists():
            print(f"Warning: description file not found: {path}")
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
            if isinstance(data, dict):
                self._descriptions = data
        except Exception as exc:
            print(f"Warning: failed to load descriptions: {exc}")

    def get_description(self, command: str) -> Optional[dict]:
        return self._descriptions.get(command)

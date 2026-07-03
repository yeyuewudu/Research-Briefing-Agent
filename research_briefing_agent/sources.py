from pathlib import Path
from typing import Iterable, List


def read_source_notes(paths: Iterable[Path]) -> List[str]:
    notes = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError("Source file not found: {0}".format(path))
        if not path.is_file():
            raise ValueError("Source path is not a file: {0}".format(path))
        notes.extend(_read_lines(path))
    return notes


def _read_lines(path: Path) -> List[str]:
    content = path.read_text(encoding="utf-8")
    return [line.strip("-* \t") for line in content.splitlines() if line.strip()]

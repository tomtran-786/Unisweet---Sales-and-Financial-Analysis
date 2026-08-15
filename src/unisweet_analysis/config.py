from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    sales_dir: Path
    mapping_file: Path
    settings_file: Path
    output_dir: Path

    @classmethod
    def from_root(cls, project_root: Path, output_dir: Path | None = None) -> "ProjectPaths":
        root = project_root.resolve()
        input_dir = root / "inputs"
        return cls(
            root=root,
            sales_dir=input_dir / "sales",
            mapping_file=input_dir / "mapping" / "Master Mapping.xlsx",
            settings_file=root / "config" / "settings.json",
            output_dir=(output_dir or root / "outputs").resolve(),
        )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

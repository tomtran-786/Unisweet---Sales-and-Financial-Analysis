from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_MARKET_PERIOD = re.compile(
    r"MAT[ _-]+([A-Za-z]{3})[' _-]?(\d{2}|\d{4})",
    re.IGNORECASE,
)
_MONTH_NUMBER = {
    month: number
    for number, month in enumerate(
        ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"],
        start=1,
    )
}


def parse_market_period(path: Path) -> tuple[int, int] | None:
    match = _MARKET_PERIOD.search(path.stem)
    if not match:
        return None
    raw_year = int(match.group(2))
    year = raw_year + 2000 if raw_year < 100 else raw_year
    month = _MONTH_NUMBER.get(match.group(1).upper())
    return (year, month) if month else None


def _latest_market_file(market_dir: Path) -> Path:
    files = [path for path in market_dir.glob("*.xlsx") if not path.name.startswith("~$")]
    if not files:
        raise FileNotFoundError(f"No Market workbook found in {market_dir}")
    return max(
        files,
        key=lambda path: (
            parse_market_period(path) is not None,
            parse_market_period(path) or (0, 0),
            path.stat().st_mtime_ns,
            path.name,
        ),
    )


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    sales_dir: Path
    mapping_file: Path
    pnl_file: Path
    market_file: Path
    settings_file: Path
    story_file: Path
    output_dir: Path

    @classmethod
    def from_root(cls, project_root: Path, output_dir: Path | None = None) -> "ProjectPaths":
        root = project_root.resolve()
        input_dir = root / "inputs"
        return cls(
            root=root,
            sales_dir=input_dir / "sales",
            mapping_file=input_dir / "mapping" / "Master Mapping.xlsx",
            pnl_file=input_dir / "pnl" / "P&L Table.xlsx",
            market_file=_latest_market_file(input_dir / "market"),
            settings_file=root / "config" / "settings.json",
            story_file=root / "config" / "story.json",
            output_dir=(output_dir or root / "outputs").resolve(),
        )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

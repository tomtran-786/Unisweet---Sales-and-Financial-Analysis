from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from unisweet_analysis.pipeline import run_analysis


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="session")
def generated(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict, dict, Path]:
    output_dir = tmp_path_factory.mktemp("finance_analysis") / "outputs"
    source_files = sorted((PROJECT_ROOT / "inputs").glob("**/*.xlsx"))
    hashes_before = {path: _hash(path) for path in source_files}
    summary = run_analysis(PROJECT_ROOT, output_dir=output_dir)
    hashes_after = {path: _hash(path) for path in source_files}
    assert hashes_before == hashes_after
    pack = json.loads((output_dir / "analysis_pack.json").read_text(encoding="utf-8"))
    return summary, pack, output_dir

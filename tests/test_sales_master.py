from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "build_sales_master.py"
SPEC = importlib.util.spec_from_file_location("build_sales_master", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
build_sales_master = MODULE.build_sales_master


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_sales_master_is_flat_mapped_and_preserves_governed_inputs(tmp_path: Path) -> None:
    pnl = PROJECT_ROOT / "inputs" / "pnl" / "P&L Table.xlsx"
    market = PROJECT_ROOT / "inputs" / "market" / "Market Report MAT Nov'24.xlsx"
    hashes_before = {pnl: _hash(pnl), market: _hash(market)}
    output = tmp_path / "sales_master.csv"

    result = build_sales_master(PROJECT_ROOT, output_path=output)
    master = pd.read_csv(output, dtype={"customer_code": str})

    assert result["source_file_count"] == 27
    assert result["source_record_count"] == 20_538
    assert result["master_row_count"] == 10_175
    assert result["certified_row_count"] == 9_788
    assert result["invalid_row_count"] == 387
    assert master["customer_code"].str.len().eq(8).all()
    assert master[["customer_name", "channel_code", "brand_name", "product_name"]].notna().all().all()
    assert (master.loc[master["certified_for_analysis"], "gsv_keur"] >= master.loc[master["certified_for_analysis"], "turnover_keur"]).all()
    assert set(master["data_quality_status"]) == {"VALID", "REVIEW", "INVALID"}
    assert hashes_before == {pnl: _hash(pnl), market: _hash(market)}

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "storyline_metrics.py"
SPEC = importlib.util.spec_from_file_location("storyline_metrics", SCRIPT_PATH)
assert SPEC and SPEC.loader
metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metrics)

DATA = metrics.STORYLINE_DATAFRAMES


def test_raw_sales_reconciles_to_pnl_by_total_and_brand() -> None:
    reconciliation = DATA["pnl_reconciliation"]
    check_columns = [column for column in reconciliation if column.startswith("check_")]
    assert np.allclose(reconciliation[check_columns], 0.0, atol=1e-8)

    sales = metrics._load_sales()
    pnl = DATA["pnl"].set_index("brand")
    for brand in ["OLIVE", "COBALT", "SKY"]:
        for year in [metrics.PRIOR_YEAR, metrics.CURRENT_YEAR]:
            rows = sales.loc[
                sales["brand_name"].eq(brand) & sales["reporting_year"].eq(year)
            ]
            assert rows["gsv_keur"].sum() == pytest.approx(pnl.loc[brand, f"gsv_{year}_keur"])
            assert rows["turnover_keur"].sum() == pytest.approx(
                pnl.loc[brand, f"turnover_{year}_keur"]
            )
            assert rows["discount_keur"].sum() == pytest.approx(
                pnl.loc[brand, f"discount_{year}_keur"]
            )


def test_headlines_and_turnover_bridge_match_storyline() -> None:
    headline = DATA["headline"].set_index("metric")
    assert headline.loc["GSV", "value_2024"] == pytest.approx(349_247.6)
    assert headline.loc["Turnover", "value_2024"] == pytest.approx(270_504.3)
    assert headline.loc["Discount / GSV", "value_2024"] == pytest.approx(0.225466, abs=1e-6)
    assert (
        headline.loc["Discount / GSV", "value_2024"]
        - headline.loc["Discount / GSV", "value_2023"]
    ) * 10_000 == pytest.approx(62.0526, abs=1e-3)
    assert headline.loc["PBO", "value_2024"] == pytest.approx(85_921.745)

    bridge = DATA["topline_bridge"]
    assert bridge.loc[1, "value_keur"] == pytest.approx(-17_395.4274, abs=1e-3)
    assert bridge.loc[2, "value_keur"] == pytest.approx(-2_167.1726, abs=1e-3)
    assert bridge.loc[0, "value_keur"] + bridge.loc[1:2, "value_keur"].sum() == pytest.approx(
        bridge.loc[3, "value_keur"]
    )


def test_market_share_and_channel_metrics_reconcile() -> None:
    bridge = DATA["market_share_bridge"]
    assert bridge.loc[1, "value_pp"] == pytest.approx(-2.97735)
    assert bridge.loc[2, "value_pp"] == pytest.approx(0.44965)
    assert bridge.loc[3, "value_pp"] == pytest.approx(0.55890)
    assert bridge.loc[4, "step"] == "Source rounding"
    assert abs(bridge.loc[4, "value_pp"]) < 0.002
    assert bridge.loc[0, "value_pp"] + bridge.loc[1:4, "value_pp"].sum() == pytest.approx(
        bridge.loc[5, "value_pp"]
    )

    channel = DATA["channel"].set_index("channel")
    assert channel.loc["MT", "share_movement_pp"] == pytest.approx(-6.07085)
    assert channel.loc["DT", "share_movement_pp"] == pytest.approx(-0.27830)
    assert channel.loc["MT", "competitor"] == "LILAC"
    assert channel.loc["DT", "competitor"] == "NAVY"
    assert abs(channel.loc["DT", "to_change_keur"]) > abs(channel.loc["MT", "to_change_keur"])
    assert channel.loc["MT", "to_growth_pct"] < channel.loc["DT", "to_growth_pct"]


def test_h2_customer_product_and_customer_sku_concentration() -> None:
    monthly = DATA["monthly"]
    total_decline = monthly["to_change_keur"].sum()
    h2_decline = monthly.loc[monthly["half"].eq("H2"), "to_change_keur"].sum()
    assert h2_decline / total_decline == pytest.approx(0.9570, abs=1e-4)
    assert monthly.loc[monthly["month_number"].eq(2), "to_change_keur"].iat[0] == pytest.approx(-7_482.1)

    customer = DATA["customer"].set_index("customer_name")
    top_three = customer.loc[["Bliss", "Candies", "Macarons"], "to_change_keur"].sum()
    assert top_three / total_decline == pytest.approx(0.9056, abs=1e-4)

    product = DATA["product"].set_index("product_name")
    assert product.loc["POUCH 900GR", "to_change_keur"] == pytest.approx(-13_042.3)
    assert product.loc["PACK 1.1KG", "to_change_keur"] == pytest.approx(-10_502.7)
    assert product.loc["POUCH 400GR", "to_change_keur"] == pytest.approx(6_035.7)

    customer_sku = DATA["customer_sku"].set_index(["customer_name", "product_name"])
    assert customer_sku.loc[("Bliss", "POUCH 900GR"), "to_change_keur"] == pytest.approx(-5_649.0)
    assert customer_sku.loc[("Macarons", "POUCH 900GR"), "to_change_keur"] == pytest.approx(-2_661.5)
    assert customer_sku.loc[("Candies", "PACK 1.1KG"), "to_change_keur"] == pytest.approx(-3_211.5)


def test_pbo_bridge_and_supply_chain_rate_caveat() -> None:
    bridge = DATA["pbo_bridge"]
    assert bridge.loc[1, "value_keur"] == pytest.approx(-10_302.11)
    assert bridge.loc[2, "value_keur"] == pytest.approx(15_500.0)
    assert bridge.loc[0, "value_keur"] + bridge.loc[1:2, "value_keur"].sum() == pytest.approx(
        bridge.loc[3, "value_keur"]
    )

    total = DATA["pnl"].set_index("brand").loc["TOTAL"]
    assert total["pbo_growth_pct"] == pytest.approx(0.064391, abs=1e-6)
    assert total["pbo_margin_movement_bps"] == pytest.approx(393.4147, abs=1e-3)
    assert total["supply_chain_2024_keur"] - total["supply_chain_2023_keur"] == pytest.approx(
        -9_260.49
    )
    assert total["supply_chain_pct_to_movement_bps"] == pytest.approx(34.984, abs=1e-3)


def test_flagged_rows_are_retained_and_visible() -> None:
    quality = DATA["quality"].set_index("metric")
    assert quality.loc["Flagged TO > GSV TO FY2023", "value"] == pytest.approx(2_574.5)
    assert quality.loc["Flagged TO > GSV TO FY2024", "value"] == pytest.approx(3_173.0)

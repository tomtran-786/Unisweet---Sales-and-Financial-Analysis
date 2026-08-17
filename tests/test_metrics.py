from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "metrics.py"
SPEC = importlib.util.spec_from_file_location("unisweet_metrics", SCRIPT_PATH)
assert SPEC and SPEC.loader
metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metrics)


def _total_row(frame: pd.DataFrame) -> pd.Series:
    return frame.loc[frame["dimension"].eq("Total")].iloc[0]


def test_annual_sales_headlines_use_latest_complete_years() -> None:
    assert metrics.PRIOR_YEAR == 2023
    assert metrics.CURRENT_YEAR == 2024

    turnover = _total_row(metrics.turnover_metrics_df)
    gsv = _total_row(metrics.gsv_metrics_df)

    assert turnover["current_to_keur"] == pytest.approx(267_331.3)
    assert turnover["prior_to_keur"] == pytest.approx(287_492.4)
    assert turnover["to_change_keur"] == pytest.approx(-20_161.1)
    assert turnover["to_growth_pct"] == pytest.approx(-0.0701274190)

    assert gsv["current_gsv_keur"] == pytest.approx(346_420.6)
    assert gsv["prior_gsv_keur"] == pytest.approx(369_112.5)
    assert gsv["gsv_change_keur"] == pytest.approx(-22_691.9)
    assert gsv["gsv_growth_pct"] == pytest.approx(-0.0614769210)


def test_change_names_and_driver_contributions_reconcile() -> None:
    legacy_term = "vari" + "ance"
    for frame in metrics.METRIC_DATAFRAMES.values():
        assert not any(legacy_term in column.lower() for column in frame.columns)

    expected_total = _total_row(metrics.turnover_metrics_df)["to_change_keur"]
    for _, dimension in metrics.driver_contribution_df.groupby("dimension"):
        assert dimension["to_change_keur"].sum() == pytest.approx(expected_total)
        assert dimension["change_contribution_pct"].sum() == pytest.approx(1.0)


def test_annual_mix_discount_and_penetration_use_period_aggregates() -> None:
    mix_totals = metrics.product_pack_mix_df.groupby(
        ["dimension", "mix_scope_key"], dropna=False
    )[["current_to_mix_pct", "prior_to_mix_pct"]].sum()
    assert np.allclose(mix_totals["current_to_mix_pct"], 1.0)
    assert np.allclose(mix_totals["prior_to_mix_pct"], 1.0)

    discount = _total_row(metrics.discount_metrics_df)
    assert discount["current_discount_pct_to"] == pytest.approx(
        discount["current_discount_keur"] / discount["current_to_keur"]
    )
    assert discount["prior_discount_pct_to"] == pytest.approx(
        discount["prior_discount_keur"] / discount["prior_to_keur"]
    )
    assert discount["current_discount_pct_gsv"] == pytest.approx(
        discount["current_discount_keur"] / discount["current_gsv_keur"]
    )
    assert discount["prior_discount_pct_gsv"] == pytest.approx(
        discount["prior_discount_keur"] / discount["prior_gsv_keur"]
    )

    penetration_columns = [
        "current_customer_penetration_pct",
        "prior_customer_penetration_pct",
    ]
    penetration = metrics.customer_penetration_df[penetration_columns]
    assert penetration.ge(0).all().all()
    assert penetration.le(1).all().all()


def test_monthly_volatility_has_complete_aligned_series_and_reconciles() -> None:
    volatility = metrics.sales_volatility_df
    assert len(volatility) == 72
    assert volatility.groupby(["dimension", "entity_key"]).size().eq(12).all()
    assert set(volatility["month_number"]) == set(range(1, 13))
    assert volatility["current_month"].dt.year.eq(metrics.CURRENT_YEAR).all()
    assert volatility["prior_month"].dt.year.eq(metrics.PRIOR_YEAR).all()

    annual_frames = {
        "turnover_keur": metrics.turnover_metrics_df,
        "gsv_keur": metrics.gsv_metrics_df,
        "discount_keur": metrics.discount_metrics_df,
    }
    for value_name, annual_frame in annual_frames.items():
        monthly = volatility.groupby(["dimension", "entity_key"], as_index=False)[
            [f"current_{value_name}", f"prior_{value_name}"]
        ].sum()
        annual = annual_frame.loc[
            annual_frame["dimension"].isin(["Total", "Brand", "Channel"]),
            [
                "dimension",
                "entity_key",
                f"current_{value_name.replace('turnover', 'to')}",
                f"prior_{value_name.replace('turnover', 'to')}",
            ],
        ].rename(
            columns={
                f"current_{value_name.replace('turnover', 'to')}": "annual_current",
                f"prior_{value_name.replace('turnover', 'to')}": "annual_prior",
            }
        )
        reconciled = monthly.merge(
            annual, on=["dimension", "entity_key"], how="outer", validate="one_to_one"
        )
        assert np.allclose(
            reconciled[f"current_{value_name}"], reconciled["annual_current"]
        )
        assert np.allclose(
            reconciled[f"prior_{value_name}"], reconciled["annual_prior"]
        )

    total = volatility.loc[volatility["dimension"].eq("Total")]
    assert np.allclose(
        total["current_discount_pct_gsv"],
        total["current_discount_keur"] / total["current_gsv_keur"],
    )
    assert np.allclose(
        total["prior_discount_pct_gsv"],
        total["prior_discount_keur"] / total["prior_gsv_keur"],
    )


def test_standalone_reconciliation_checks_still_hold() -> None:
    assert np.allclose(metrics.pnl_metrics_df["pbo_bridge_check_eur"], 0.0)
    assert (
        metrics.market_metrics_df["sales_value_gain_loss_matches_source"].dropna().all()
    )
    assert metrics.market_metrics_df["share_gain_loss_matches_source"].dropna().all()

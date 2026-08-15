from __future__ import annotations

import pytest


def test_current_financial_result_and_quality_gate(generated: tuple[dict, dict, object]) -> None:
    summary, pack, _ = generated
    kpi = pack["kpis"]

    assert summary["publication_status"] == "READY"
    assert summary["critical_failure_count"] == 0
    assert summary["sales_source_file_count"] == 27
    assert summary["source_file_count"] == 30
    assert summary["quarantine_row_count"] == 387
    assert pack["metadata"]["comparison_basis"] == "YOY"
    assert pack["metadata"]["reporting_month"] == "2024-12-01"
    assert kpi["current_turnover_keur"] == pytest.approx(22_461.0)
    assert kpi["turnover_variance_keur"] == pytest.approx(-2_537.5)
    assert kpi["turnover_growth_pct"] == pytest.approx(-0.101506, abs=1e-6)
    assert kpi["current_discount_pct_to"] == pytest.approx(0.247562, abs=1e-6)
    assert kpi["discount_pct_to_movement_bps"] == pytest.approx(-312.463, abs=1e-3)
    assert kpi["current_pbo_keur"] == pytest.approx(85_921.745)
    assert kpi["pbo_variance_keur"] == pytest.approx(5_197.89)


def test_pack_has_three_evidence_backed_actions(generated: tuple[dict, dict, object]) -> None:
    _, pack, _ = generated
    insights = pack["insights"]
    required = {
        "headline",
        "evidence",
        "financial_impact_keur",
        "impact_basis",
        "recommended_action",
        "proposed_owner",
        "timing",
        "caveat",
    }
    assert [insight["rank"] for insight in insights] == [1, 2, 3]
    assert all(required.issubset(insight) for insight in insights)
    assert all(insight["evidence"] and insight["recommended_action"] for insight in insights)


def test_all_critical_checks_pass_and_bridge_reconciles(generated: tuple[dict, dict, object]) -> None:
    _, pack, _ = generated
    critical = [check for check in pack["checks"] if check["blocking"]]
    assert critical
    assert all(check["status"] == "PASS" for check in critical)
    bridge = pack["gross_to_net_bridge"]
    assert bridge[0]["value_keur"] + bridge[1]["value_keur"] + bridge[2]["value_keur"] == pytest.approx(
        bridge[3]["value_keur"]
    )

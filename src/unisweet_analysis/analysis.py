from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd


PNL_METRICS = [
    "gsv_keur",
    "discount_keur",
    "turnover_keur",
    "supply_chain_cost_keur",
    "gross_profit_keur",
    "marketing_expense_keur",
    "pbo_keur",
]


def _check(
    check_id: str,
    area: str,
    name: str,
    severity: str,
    exceptions: int,
    details: str,
) -> dict[str, Any]:
    blocking = severity == "CRITICAL"
    status = "PASS" if exceptions == 0 else ("FAIL" if blocking else "WARN")
    return {
        "check_id": check_id,
        "area": area,
        "name": name,
        "severity": severity,
        "status": status,
        "blocking": blocking,
        "exceptions": int(exceptions),
        "details": details,
    }


def _native(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        return None
    return value


def records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {column: _native(value) for column, value in row.items()}
        for row in frame.to_dict(orient="records")
    ]


def _prepare_sales(
    raw: pd.DataFrame,
    customers: pd.DataFrame,
    brands: pd.DataFrame,
    products: pd.DataFrame,
    source_schema_failures: int,
    minimum_sales_files: int,
    actual_sales_files: int,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, Any]]]:
    checks: list[dict[str, Any]] = []
    checks.append(
        _check(
            "SOURCE_FILE_COUNT",
            "Source",
            f"At least {minimum_sales_files} Sales workbooks",
            "CRITICAL",
            max(minimum_sales_files - actual_sales_files, 0),
            f"Minimum {minimum_sales_files}; received {actual_sales_files}.",
        )
    )
    checks.append(
        _check(
            "SOURCE_SCHEMA",
            "Source",
            "All workbooks match the expected source contract",
            "CRITICAL",
            source_schema_failures,
            f"Source workbooks with invalid schema: {source_schema_failures}.",
        )
    )
    required_columns = [
        "customer_code",
        "brand_code",
        "pack_type",
        "pack_size",
        "reporting_month",
        "metric_code",
        "metric_value_keur",
    ]
    required_errors = int(raw[required_columns].isna().any(axis=1).sum()) if not raw.empty else 1
    checks.append(
        _check(
            "SALES_REQUIRED_VALUES",
            "Sales",
            "Required Sales fields and types are populated",
            "CRITICAL",
            required_errors,
            f"Rows with missing required values: {required_errors}.",
        )
    )
    unsupported = int((~raw["metric_code"].isin(["GSV", "TURNOVER"])).sum()) if not raw.empty else 1
    checks.append(
        _check(
            "SALES_KPI_DOMAIN",
            "Sales",
            "Only GSV and Turnover KPI labels are accepted",
            "CRITICAL",
            unsupported,
            f"Rows with unsupported KPI labels: {unsupported}.",
        )
    )

    grain = ["reporting_month", "customer_code", "brand_code", "product_key", "pack_type", "pack_size"]
    valid_raw = raw[raw["metric_code"].isin(["GSV", "TURNOVER"])].copy()
    aggregated = (
        valid_raw.groupby(grain + ["metric_code"], dropna=False)
        .agg(metric_value_keur=("metric_value_keur", "sum"), record_count=("metric_value_keur", "size"))
        .reset_index()
    )
    values = aggregated.pivot(index=grain, columns="metric_code", values="metric_value_keur").reset_index()
    counts = aggregated.pivot(index=grain, columns="metric_code", values="record_count").reset_index()
    values.columns.name = None
    counts.columns.name = None
    values = values.rename(columns={"GSV": "gsv_keur", "TURNOVER": "turnover_keur"})
    counts = counts.rename(columns={"GSV": "gsv_count", "TURNOVER": "turnover_count"})
    paired = values.merge(counts, on=grain, how="outer")
    for column in ["gsv_keur", "turnover_keur", "gsv_count", "turnover_count"]:
        if column not in paired:
            paired[column] = 0
    paired[["gsv_count", "turnover_count"]] = paired[["gsv_count", "turnover_count"]].fillna(0)

    missing_pairs = int(((paired["gsv_count"] == 0) | (paired["turnover_count"] == 0)).sum())
    duplicate = (paired["gsv_count"] > 1) | (paired["turnover_count"] > 1)
    nonzero = paired[["gsv_keur", "turnover_keur"]].fillna(0).abs().max(axis=1) > 0.01
    duplicate_nonzero = int((duplicate & nonzero).sum())
    duplicate_zero = int((duplicate & ~nonzero).sum())
    turnover_gt_gsv = int((paired["turnover_keur"] > paired["gsv_keur"]).sum())
    checks.extend(
        [
            _check(
                "SALES_KPI_PAIRS",
                "Sales",
                "Every business grain has one GSV and one Turnover record",
                "CRITICAL",
                missing_pairs + duplicate_nonzero,
                f"Missing KPI pairs: {missing_pairs}; non-zero duplicate pairs: {duplicate_nonzero}.",
            ),
            _check(
                "SALES_DUPLICATE_ZERO",
                "Sales",
                "Zero-value duplicate grains are disclosed",
                "WARNING",
                duplicate_zero,
                f"Zero-value duplicate grains quarantined: {duplicate_zero}.",
            ),
            _check(
                "SALES_TURNOVER_GT_GSV",
                "Sales",
                "Turnover greater than GSV is disclosed",
                "WARNING",
                turnover_gt_gsv,
                f"Grains quarantined because Turnover exceeds GSV: {turnover_gt_gsv}.",
            ),
        ]
    )

    paired = paired.merge(customers, on="customer_code", how="left")
    paired = paired.merge(brands, on="brand_code", how="left")
    paired = paired.merge(
        products[["product_key", "product_name", "product_group_lv1", "product_group_lv2", "mapping_review_required"]],
        on="product_key",
        how="left",
    )
    mapping_errors = int(
        paired[["channel_code", "customer_name", "brand_name", "product_name"]].isna().any(axis=1).sum()
    )
    checks.append(
        _check(
            "MAPPING_COVERAGE",
            "Mapping",
            "Customer, Brand and exact Product mappings cover Sales",
            "CRITICAL",
            mapping_errors,
            f"Sales grains with incomplete mapping: {mapping_errors}.",
        )
    )
    mapping_review = int(products["mapping_review_required"].fillna(False).sum())
    checks.append(
        _check(
            "MAPPING_REVIEW",
            "Mapping",
            "Ambiguous LV2 labels remain visible for review",
            "WARNING",
            mapping_review,
            f"Product mapping rows requiring business review: {mapping_review}; exact product keys remain usable.",
        )
    )

    invalid_pair = (
        (paired["gsv_count"] != 1)
        | (paired["turnover_count"] != 1)
        | (paired["turnover_keur"] > paired["gsv_keur"])
        | paired[["channel_code", "customer_name", "brand_name", "product_name"]].isna().any(axis=1)
    )
    quarantine = paired[invalid_pair].copy()
    quarantine["reason"] = quarantine.apply(
        lambda row: "; ".join(
            reason
            for condition, reason in [
                (row["gsv_count"] != 1, "GSV_COUNT_NOT_ONE"),
                (row["turnover_count"] != 1, "TURNOVER_COUNT_NOT_ONE"),
                (row["turnover_keur"] > row["gsv_keur"], "TURNOVER_GT_GSV"),
                (pd.isna(row["channel_code"]), "CUSTOMER_MAPPING_MISSING"),
                (pd.isna(row["brand_name"]), "BRAND_MAPPING_MISSING"),
                (pd.isna(row["product_name"]), "PRODUCT_MAPPING_MISSING"),
            ]
            if condition
        ),
        axis=1,
    )
    certified = paired[~invalid_pair].copy()
    certified["discount_keur"] = certified["gsv_keur"] - certified["turnover_keur"]
    certified["discount_pct_to"] = certified["discount_keur"] / certified["turnover_keur"].replace(0, np.nan)
    certified["discount_pct_gsv"] = certified["discount_keur"] / certified["gsv_keur"].replace(0, np.nan)
    reconciliation = float((certified["gsv_keur"] - certified["discount_keur"] - certified["turnover_keur"]).abs().max())
    checks.append(
        _check(
            "GROSS_TO_NET_RECONCILIATION",
            "Finance",
            "GSV minus Discount equals Turnover",
            "CRITICAL",
            int(reconciliation > 0.01),
            f"Maximum certified Gross-to-Net delta: {reconciliation:.6f} kEUR.",
        )
    )
    negative_values = int((raw["metric_value_keur"] < 0).sum())
    checks.append(
        _check(
            "SALES_NEGATIVE_VALUES",
            "Sales",
            "Negative Sales values are disclosed",
            "WARNING",
            negative_values,
            f"Negative source KPI rows retained: {negative_values}.",
        )
    )
    return certified, quarantine, checks


def _pnl_checks(
    pnl: pd.DataFrame,
    raw_sales: pd.DataFrame,
    certified_sales: pd.DataFrame,
    brands: pd.DataFrame,
    tolerance: float,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    incomplete = int(pnl[PNL_METRICS].isna().any(axis=1).sum())
    checks.append(
        _check(
            "PNL_COMPLETENESS",
            "P&L",
            "Every Brand × Year has all governed P&L metrics",
            "CRITICAL",
            incomplete,
            f"Incomplete Brand × Year P&L rows: {incomplete}.",
        )
    )
    formula_delta = max(
        float((pnl["gross_profit_keur"] - (pnl["turnover_keur"] - pnl["supply_chain_cost_keur"])).abs().max()),
        float((pnl["pbo_keur"] - (pnl["gross_profit_keur"] - pnl["marketing_expense_keur"])).abs().max()),
    )
    checks.append(
        _check(
            "PNL_FORMULAS",
            "P&L",
            "Gross Profit and PBO equations reconcile",
            "CRITICAL",
            int(formula_delta > tolerance),
            f"Maximum P&L formula delta: {formula_delta:.6f} kEUR.",
        )
    )

    source_year = raw_sales.copy()
    source_year["reporting_year"] = source_year["reporting_year"].astype(int)
    source_year = (
        source_year.groupby(["reporting_year", "brand_code", "metric_code"], dropna=False)["metric_value_keur"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
        .rename(columns={"GSV": "source_gsv_keur", "TURNOVER": "source_turnover_keur"})
        .merge(brands, on="brand_code", how="left")
    )
    tie = pnl.merge(
        source_year[["reporting_year", "brand_name", "source_gsv_keur", "source_turnover_keur"]],
        on=["reporting_year", "brand_name"],
        how="left",
    )
    tie["max_delta"] = tie[["gsv_keur", "turnover_keur"]].sub(
        tie[["source_gsv_keur", "source_turnover_keur"]].set_axis(["gsv_keur", "turnover_keur"], axis=1)
    ).abs().max(axis=1)
    tie_errors = int((tie["max_delta"] > tolerance).sum() + tie["max_delta"].isna().sum())
    checks.append(
        _check(
            "SALES_TO_PNL_RECONCILIATION",
            "P&L",
            "Source annual Sales ties to P&L by Brand and Year",
            "CRITICAL",
            tie_errors,
            f"Brand × Year combinations outside tolerance: {tie_errors}.",
        )
    )

    first_pnl_year = int(pnl["reporting_year"].min())
    sales_coverage = certified_sales.assign(
        reporting_year=certified_sales["reporting_month"].dt.year
    )[["reporting_year", "brand_name"]].drop_duplicates()
    sales_coverage = sales_coverage[sales_coverage["reporting_year"] >= first_pnl_year]
    coverage = sales_coverage.merge(
        pnl[["reporting_year", "brand_name"]].drop_duplicates(),
        on=["reporting_year", "brand_name"],
        how="left",
        indicator=True,
    )
    coverage_errors = int((coverage["_merge"] != "both").sum())
    checks.append(
        _check(
            "PNL_PERIOD_COVERAGE",
            "P&L",
            "P&L covers Sales Brand × Year from the first P&L year",
            "CRITICAL",
            coverage_errors,
            f"Sales Brand × Year combinations missing from P&L: {coverage_errors}.",
        )
    )
    return checks


def _market_checks(market: pd.DataFrame, tolerance: float) -> list[dict[str, Any]]:
    period_errors = int(market[["reporting_period", "reporting_date"]].isna().any(axis=1).sum())
    total = market[market["channel_code"] == "TOTAL"]
    channels = (
        market[market["channel_code"] != "TOTAL"]
        .groupby(["row_type", "segment_name", "manufacturer_name", "brand_name"], dropna=False)[
            ["sales_value_mat_1_meur", "sales_value_mat_meur"]
        ]
        .sum()
        .reset_index()
    )
    comparison = total.merge(
        channels,
        on=["row_type", "segment_name", "manufacturer_name", "brand_name"],
        how="left",
        suffixes=("_total", "_channels"),
    )
    mismatch = (
        (comparison["sales_value_mat_1_meur_total"] - comparison["sales_value_mat_1_meur_channels"]).abs() > tolerance
    ) | (
        (comparison["sales_value_mat_meur_total"] - comparison["sales_value_mat_meur_channels"]).abs() > tolerance
    )
    return [
        _check(
            "MARKET_PERIOD",
            "Market",
            "Market period is parsed from the source filename",
            "CRITICAL",
            period_errors,
            f"Market rows without reporting period: {period_errors}.",
        ),
        _check(
            "MARKET_TOTAL_DISCLOSURE",
            "Market",
            "Total versus channel gaps are disclosed",
            "WARNING",
            int(mismatch.sum()),
            f"Total rows not equal to the sum of channels: {int(mismatch.sum())}; explicit Total rows remain the overall source.",
        ),
    ]


def _period_comparison(sales: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp, str]:
    months = sorted(pd.Timestamp(value) for value in sales["reporting_month"].dropna().unique())
    current = months[-1]
    yoy = current - pd.DateOffset(years=1)
    if yoy in months:
        return current, yoy, "YOY"
    prior = current - pd.DateOffset(months=1)
    if prior in months:
        return current, prior, "MOM"
    raise ValueError("At least two comparable Sales months are required")


def _overall_scorecard(sales: pd.DataFrame, current: pd.Timestamp, prior: pd.Timestamp) -> dict[str, Any]:
    def totals(month: pd.Timestamp) -> pd.Series:
        return sales[sales["reporting_month"] == month][["gsv_keur", "discount_keur", "turnover_keur"]].sum()

    current_values = totals(current)
    prior_values = totals(prior)
    result: dict[str, Any] = {}
    for metric in ["gsv_keur", "discount_keur", "turnover_keur"]:
        name = metric.removesuffix("_keur")
        current_value = float(current_values[metric])
        prior_value = float(prior_values[metric])
        result[f"current_{name}_keur"] = current_value
        result[f"prior_{name}_keur"] = prior_value
        result[f"{name}_variance_keur"] = current_value - prior_value
        result[f"{name}_growth_pct"] = current_value / prior_value - 1 if prior_value else None
    result["current_discount_pct_to"] = result["current_discount_keur"] / result["current_turnover_keur"]
    result["prior_discount_pct_to"] = result["prior_discount_keur"] / result["prior_turnover_keur"]
    result["discount_pct_to_movement_bps"] = (
        result["current_discount_pct_to"] - result["prior_discount_pct_to"]
    ) * 10_000
    return result


def _drivers(sales: pd.DataFrame, current: pd.Timestamp, prior: pd.Timestamp) -> pd.DataFrame:
    dimensions = [
        ("BRAND", "brand_code", "brand_name"),
        ("CHANNEL", "channel_code", "channel_code"),
        ("CUSTOMER", "customer_code", "customer_name"),
        ("PRODUCT", "product_key", "product_name"),
    ]
    frames = []
    overall_variance = float(
        sales[sales["reporting_month"] == current]["turnover_keur"].sum()
        - sales[sales["reporting_month"] == prior]["turnover_keur"].sum()
    )
    for dimension, id_column, name_column in dimensions:
        dimension_columns = [id_column] if id_column == name_column else [id_column, name_column]
        frame = (
            sales[sales["reporting_month"].isin([current, prior])]
            .groupby(["reporting_month", *dimension_columns], dropna=False)["turnover_keur"]
            .sum()
            .unstack("reporting_month", fill_value=0)
            .reset_index()
        )
        for month in [prior, current]:
            if month not in frame:
                frame[month] = 0.0
        frame = frame.rename(columns={id_column: "dimension_id", prior: "prior_turnover_keur", current: "current_turnover_keur"})
        if id_column == name_column:
            frame["dimension_name"] = frame["dimension_id"]
        else:
            frame = frame.rename(columns={name_column: "dimension_name"})
        frame["analysis_dimension"] = dimension
        frame["turnover_variance_keur"] = frame["current_turnover_keur"] - frame["prior_turnover_keur"]
        frame["turnover_growth_pct"] = frame["current_turnover_keur"] / frame["prior_turnover_keur"].replace(0, np.nan) - 1
        frame["variance_contribution_pct"] = frame["turnover_variance_keur"] / overall_variance if overall_variance else np.nan
        frame["driver_rank"] = frame["turnover_variance_keur"].abs().rank(method="first", ascending=False).astype(int)
        frames.append(frame[["analysis_dimension", "dimension_id", "dimension_name", "prior_turnover_keur", "current_turnover_keur", "turnover_variance_keur", "turnover_growth_pct", "variance_contribution_pct", "driver_rank"]])
    return pd.concat(frames, ignore_index=True).sort_values(["analysis_dimension", "driver_rank"])


def _leakage(sales: pd.DataFrame, current: pd.Timestamp, prior: pd.Timestamp) -> pd.DataFrame:
    dimensions = [
        ("BRAND", "brand_code", "brand_name"),
        ("CHANNEL", "channel_code", "channel_code"),
        ("CUSTOMER", "customer_code", "customer_name"),
        ("PRODUCT", "product_key", "product_name"),
    ]
    frames = []
    for dimension, id_column, name_column in dimensions:
        dimension_columns = [id_column] if id_column == name_column else [id_column, name_column]
        grouped = (
            sales[sales["reporting_month"].isin([current, prior])]
            .groupby(["reporting_month", *dimension_columns], dropna=False)[["gsv_keur", "discount_keur", "turnover_keur"]]
            .sum()
            .reset_index()
        )
        current_rows = grouped[grouped["reporting_month"] == current].drop(columns="reporting_month")
        prior_rows = grouped[grouped["reporting_month"] == prior].drop(columns="reporting_month")
        frame = current_rows.merge(prior_rows, on=dimension_columns, how="outer", suffixes=("_current", "_prior")).fillna(0)
        frame = frame.rename(columns={id_column: "dimension_id"})
        if id_column == name_column:
            frame["dimension_name"] = frame["dimension_id"]
        else:
            frame = frame.rename(columns={name_column: "dimension_name"})
        frame["analysis_dimension"] = dimension
        frame["current_discount_pct_to"] = frame["discount_keur_current"] / frame["turnover_keur_current"].replace(0, np.nan)
        frame["prior_discount_pct_to"] = frame["discount_keur_prior"] / frame["turnover_keur_prior"].replace(0, np.nan)
        frame["turnover_variance_keur"] = frame["turnover_keur_current"] - frame["turnover_keur_prior"]
        frame["discount_pct_to_movement_bps"] = (frame["current_discount_pct_to"] - frame["prior_discount_pct_to"]) * 10_000
        frame["discount_improvement_opportunity_keur"] = (
            (frame["current_discount_pct_to"] - frame["prior_discount_pct_to"])
            * frame["turnover_keur_current"]
        ).clip(lower=0).fillna(0)
        frame["leakage_quadrant"] = np.select(
            [
                (frame["turnover_variance_keur"] < 0) & (frame["discount_pct_to_movement_bps"] > 0),
                (frame["turnover_variance_keur"] >= 0) & (frame["discount_pct_to_movement_bps"] > 0),
                (frame["turnover_variance_keur"] < 0) & (frame["discount_pct_to_movement_bps"] <= 0),
            ],
            ["SALES_DOWN_RATE_UP", "SALES_UP_RATE_UP", "SALES_DOWN_RATE_DOWN"],
            default="SALES_UP_RATE_DOWN",
        )
        frames.append(frame[["analysis_dimension", "dimension_id", "dimension_name", "turnover_keur_current", "turnover_keur_prior", "turnover_variance_keur", "current_discount_pct_to", "prior_discount_pct_to", "discount_pct_to_movement_bps", "discount_improvement_opportunity_keur", "leakage_quadrant"]])
    return pd.concat(frames, ignore_index=True).sort_values(
        ["discount_improvement_opportunity_keur", "turnover_variance_keur"], ascending=[False, True]
    )


def _pnl_comparison(pnl: pd.DataFrame) -> pd.DataFrame:
    base = pnl[["reporting_year", "brand_name", *PNL_METRICS]].copy()
    total = base.groupby("reporting_year", as_index=False)[PNL_METRICS].sum()
    total["brand_name"] = "TOTAL"
    combined = pd.concat([base, total], ignore_index=True)
    current_year = int(combined["reporting_year"].max())
    prior_year = current_year - 1
    current = combined[combined["reporting_year"] == current_year].drop(columns="reporting_year")
    prior = combined[combined["reporting_year"] == prior_year].drop(columns="reporting_year")
    comparison = current.merge(prior, on="brand_name", how="inner", suffixes=("_current", "_prior"))
    comparison["reporting_year"] = current_year
    comparison["prior_year"] = prior_year
    for metric in PNL_METRICS:
        base_name = metric.removesuffix("_keur")
        comparison[f"{base_name}_variance_keur"] = comparison[f"{metric}_current"] - comparison[f"{metric}_prior"]
        comparison[f"{base_name}_growth_pct"] = comparison[f"{metric}_current"] / comparison[f"{metric}_prior"].replace(0, np.nan) - 1
    comparison["current_gross_margin_pct"] = comparison["gross_profit_keur_current"] / comparison["turnover_keur_current"]
    comparison["prior_gross_margin_pct"] = comparison["gross_profit_keur_prior"] / comparison["turnover_keur_prior"]
    comparison["gross_margin_movement_bps"] = (comparison["current_gross_margin_pct"] - comparison["prior_gross_margin_pct"]) * 10_000
    comparison["current_pbo_pct_to"] = comparison["pbo_keur_current"] / comparison["turnover_keur_current"]
    comparison["prior_pbo_pct_to"] = comparison["pbo_keur_prior"] / comparison["turnover_keur_prior"]
    comparison["pbo_margin_movement_bps"] = (comparison["current_pbo_pct_to"] - comparison["prior_pbo_pct_to"]) * 10_000
    return comparison.sort_values("brand_name")


def _market_signals(sales: pd.DataFrame, market: pd.DataFrame, manufacturer: str) -> pd.DataFrame:
    annual = sales.assign(reporting_year=sales["reporting_month"].dt.year).groupby(
        ["reporting_year", "brand_name"], as_index=False
    )["turnover_keur"].sum()
    current_year = int(annual["reporting_year"].max())
    current = annual[annual["reporting_year"] == current_year].drop(columns="reporting_year")
    prior = annual[annual["reporting_year"] == current_year - 1].drop(columns="reporting_year")
    internal = current.merge(prior, on="brand_name", how="inner", suffixes=("_current", "_prior"))
    internal["internal_turnover_growth_pct"] = internal["turnover_keur_current"] / internal["turnover_keur_prior"].replace(0, np.nan) - 1
    context = market[
        (market["channel_code"] == "TOTAL")
        & (market["row_type"] == "BRAND")
        & (market["manufacturer_name"] == manufacturer.upper())
    ].copy()
    context["market_value_growth_pct"] = context["sales_value_mat_meur"] / context["sales_value_mat_1_meur"].replace(0, np.nan) - 1
    signal = internal.merge(context, on="brand_name", how="inner")
    signal["internal_calendar_year"] = current_year
    signal["sellin_vs_market_growth_gap_pp"] = (
        signal["internal_turnover_growth_pct"] - signal["market_value_growth_pct"]
    ) * 100
    signal["comparison_caveat"] = "Calendar-year internal sell-in versus supplied MAT market; directional context only"
    return signal[["brand_name", "internal_calendar_year", "turnover_keur_current", "turnover_keur_prior", "internal_turnover_growth_pct", "reporting_period", "sales_value_mat_meur", "sales_value_mat_1_meur", "market_value_growth_pct", "value_share_mat", "value_share_mat_1", "share_movement_pp", "sellin_vs_market_growth_gap_pp", "comparison_caveat"]].sort_values("brand_name")


def _signed(value: float | None, decimals: int = 0) -> str:
    return f"{float(value or 0):+,.{decimals}f}"


def _pct(value: float | None, decimals: int = 1) -> str:
    return f"{float(value or 0) * 100:+.{decimals}f}%"


def _build_insights(
    scorecard: dict[str, Any],
    comparison_basis: str,
    drivers: pd.DataFrame,
    leakage: pd.DataFrame,
    pnl: pd.DataFrame,
    market: pd.DataFrame,
) -> list[dict[str, Any]]:
    negative = drivers[drivers["turnover_variance_keur"] < 0]
    driver_evidence = []
    for dimension in ["BRAND", "CHANNEL", "PRODUCT"]:
        rows = negative[negative["analysis_dimension"] == dimension]
        if not rows.empty:
            row = rows.sort_values("turnover_variance_keur").iloc[0]
            driver_evidence.append(f"{dimension.title()} {row['dimension_name']} {_signed(row['turnover_variance_keur'])} kEUR")

    channel_leakage = leakage[
        (leakage["analysis_dimension"] == "CHANNEL")
        & (leakage["discount_improvement_opportunity_keur"] > 0)
    ]
    leakage_row = (
        channel_leakage.sort_values("discount_improvement_opportunity_keur", ascending=False).iloc[0]
        if not channel_leakage.empty
        else leakage.sort_values("discount_improvement_opportunity_keur", ascending=False).iloc[0]
    )
    total_pnl = pnl[pnl["brand_name"] == "TOTAL"].iloc[0]
    market_row = market.sort_values("sellin_vs_market_growth_gap_pp").iloc[0] if not market.empty else None

    return [
        {
            "rank": 1,
            "code": "TURNOVER_RECOVERY",
            "headline": (
                f"Turnover {_signed(scorecard['turnover_variance_keur'])} kEUR "
                f"({_pct(scorecard['turnover_growth_pct'])}) {comparison_basis} despite Discount % TO "
                f"moving {_signed(scorecard['discount_pct_to_movement_bps'])} bps."
            ),
            "evidence": "; ".join(driver_evidence),
            "financial_impact_keur": scorecard["turnover_variance_keur"],
            "impact_basis": "Current-period Turnover variance versus the governed comparison period.",
            "recommended_action": "Build a focused recovery plan around the largest Brand, Channel and Product declines; validate distribution, availability and customer sell-in before changing discount terms.",
            "proposed_owner": "Commercial Director + Sales Operations",
            "timing": "Before the next management review",
            "caveat": "Dimension cuts explain the same total variance and must not be added together.",
        },
        {
            "rank": 2,
            "code": "DISCOUNT_LEAKAGE",
            "headline": (
                f"{leakage_row['dimension_name']} combines Turnover {_signed(leakage_row['turnover_variance_keur'])} kEUR "
                f"with Discount % TO {_signed(leakage_row['discount_pct_to_movement_bps'])} bps."
            ),
            "evidence": (
                f"Current Discount % TO {float(leakage_row['current_discount_pct_to']) * 100:.1f}% vs "
                f"{float(leakage_row['prior_discount_pct_to']) * 100:.1f}%; diagnostic recovery proxy "
                f"{_signed(leakage_row['discount_improvement_opportunity_keur'])} kEUR."
            ),
            "financial_impact_keur": float(leakage_row["discount_improvement_opportunity_keur"]),
            "impact_basis": "Return to prior-period Discount % TO at current Turnover; diagnostic proxy only.",
            "recommended_action": "Review customer and product exceptions in this segment, confirm contract and promotion mechanics, then assign only validated recovery items.",
            "proposed_owner": "Sales Finance + Channel Lead",
            "timing": "Two-week leakage review",
            "caveat": "The value is not a target, forecast or causal promotion ROI estimate.",
        },
        {
            "rank": 3,
            "code": "PROFIT_QUALITY",
            "headline": (
                f"PBO {_signed(total_pnl['pbo_variance_keur'])} kEUR while Gross Profit "
                f"{_signed(total_pnl['gross_profit_variance_keur'])} kEUR; Marketing spend "
                f"{_signed(total_pnl['marketing_expense_variance_keur'])} kEUR."
            ),
            "evidence": (
                f"Gross Margin moved {_signed(total_pnl['gross_margin_movement_bps'])} bps and PBO margin "
                f"{_signed(total_pnl['pbo_margin_movement_bps'])} bps."
                + (
                    f" {market_row['brand_name']} internal growth {_pct(market_row['internal_turnover_growth_pct'])} "
                    f"vs market {_pct(market_row['market_value_growth_pct'])}."
                    if market_row is not None
                    else ""
                )
            ),
            "financial_impact_keur": float(total_pnl["pbo_variance_keur"]),
            "impact_basis": "Annual P&L variance; Market comparison is contextual and period-misaligned.",
            "recommended_action": "Separate structural productivity from deferred growth investment and require Brand-level evidence before extending marketing reductions where sell-in trails the Market.",
            "proposed_owner": "Finance Director + Marketing Director",
            "timing": "Next planning cycle",
            "caveat": "P&L is annual and Market data is MAT; neither should be allocated below its supported grain.",
        },
    ]


def build_analysis_pack(
    *,
    project_name: str,
    raw_sales: pd.DataFrame,
    customers: pd.DataFrame,
    brands: pd.DataFrame,
    products: pd.DataFrame,
    pnl: pd.DataFrame,
    market: pd.DataFrame,
    source_manifest: list[dict[str, Any]],
    settings: dict[str, Any],
) -> dict[str, Any]:
    sales_sources = [source for source in source_manifest if source["source_type"] == "sales"]
    source_schema_failures = sum(source["schema_status"] != "PASS" for source in source_manifest)
    certified, quarantine, checks = _prepare_sales(
        raw_sales,
        customers,
        brands,
        products,
        source_schema_failures,
        int(settings["minimum_sales_file_count"]),
        len(sales_sources),
    )
    checks.extend(
        _pnl_checks(
            pnl,
            raw_sales,
            certified,
            brands,
            float(settings["critical_tolerance_keur"]),
        )
    )
    checks.extend(_market_checks(market, float(settings["market_reconciliation_tolerance_meur"])))
    failed = [check for check in checks if check["blocking"] and check["status"] == "FAIL"]
    publication_status = "READY" if not failed else "BLOCKED"

    current, prior, comparison_basis = _period_comparison(certified)
    scorecard = _overall_scorecard(certified, current, prior)
    driver_frame = _drivers(certified, current, prior)
    leakage_frame = _leakage(certified, current, prior)
    pnl_frame = _pnl_comparison(pnl)
    market_frame = _market_signals(certified, market, settings["market_manufacturer"])

    trend = (
        certified.groupby("reporting_month", as_index=False)[["gsv_keur", "discount_keur", "turnover_keur"]]
        .sum()
        .sort_values("reporting_month")
        .tail(24)
    )
    brand_trend = (
        certified.groupby(["reporting_month", "brand_name"], as_index=False)["turnover_keur"]
        .sum()
        .sort_values(["reporting_month", "brand_name"])
    )
    brand_trend = brand_trend[brand_trend["reporting_month"].isin(trend["reporting_month"])]

    total_pnl = pnl_frame[pnl_frame["brand_name"] == "TOTAL"].iloc[0]
    scorecard["current_pbo_keur"] = float(total_pnl["pbo_keur_current"])
    scorecard["pbo_variance_keur"] = float(total_pnl["pbo_variance_keur"])
    scorecard["current_gross_margin_pct"] = float(total_pnl["current_gross_margin_pct"])
    scorecard["current_pbo_pct_to"] = float(total_pnl["current_pbo_pct_to"])

    gross_to_net_bridge = [
        {"step": "Prior Turnover", "value_keur": scorecard["prior_turnover_keur"], "is_total": True},
        {"step": "GSV change", "value_keur": scorecard["gsv_variance_keur"], "is_total": False},
        {"step": "Discount change", "value_keur": -scorecard["discount_variance_keur"], "is_total": False},
        {"step": "Current Turnover", "value_keur": scorecard["current_turnover_keur"], "is_total": True},
    ]
    insights = _build_insights(scorecard, comparison_basis, driver_frame, leakage_frame, pnl_frame, market_frame)
    combined_hash = hashlib.sha256(
        "\n".join(f"{source['path']}:{source['sha256']}" for source in sorted(source_manifest, key=lambda row: row["path"])).encode("utf-8")
    ).hexdigest()

    return {
        "metadata": {
            "project": project_name,
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "reporting_month": current.date().isoformat(),
            "comparison_month": prior.date().isoformat(),
            "comparison_basis": comparison_basis,
            "publication_status": publication_status,
            "critical_failure_count": len(failed),
            "input_hash": combined_hash,
            "currency": "kEUR unless stated otherwise",
            "architecture": "Excel -> Python -> analysis pack -> dashboard / approved presentation",
        },
        "kpis": {key: _native(value) for key, value in scorecard.items()},
        "gross_to_net_bridge": gross_to_net_bridge,
        "trend": records(trend),
        "brand_trend": records(brand_trend),
        "drivers": records(driver_frame[driver_frame["driver_rank"] <= 10]),
        "discount_leakage": records(leakage_frame.head(20)),
        "pnl": records(pnl_frame),
        "market": records(market_frame),
        "checks": checks,
        "source_manifest": source_manifest,
        "quarantine": {
            "row_count": int(len(quarantine)),
            "turnover_keur": float(quarantine["turnover_keur"].fillna(0).sum()),
            "records": records(quarantine[["reporting_month", "customer_code", "brand_code", "product_key", "gsv_keur", "turnover_keur", "reason"]].head(100)),
        },
        "insights": insights,
    }

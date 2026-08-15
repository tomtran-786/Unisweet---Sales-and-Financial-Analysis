from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from unisweet_analysis.config import ProjectPaths, load_json
from unisweet_analysis.loaders import load_mappings, load_sales


GRAIN_COLUMNS = [
    "reporting_month",
    "customer_code",
    "brand_code",
    "product_key",
    "pack_type",
    "pack_size",
]


def _join_unique(values: pd.Series) -> str:
    items = sorted({str(value) for value in values.dropna() if str(value).strip()})
    return ";".join(items)


def _join_rows(values: pd.Series) -> str:
    rows = sorted({int(value) for value in values.dropna()})
    return ";".join(str(value) for value in rows)


def _metric_wide(raw_sales: pd.DataFrame) -> pd.DataFrame:
    supported = raw_sales[raw_sales["metric_code"].isin(["GSV", "TURNOVER"])].copy()
    if supported.empty:
        raise ValueError("No supported GSV/Turnover Sales records were found.")

    grouped = (
        supported.groupby([*GRAIN_COLUMNS, "metric_code"], dropna=False)
        .agg(
            metric_value_keur=("metric_value_keur", "sum"),
            record_count=("metric_value_keur", "size"),
            source_files=("source_file", _join_unique),
            source_rows=("source_row", _join_rows),
        )
        .reset_index()
    )

    values = grouped.pivot(index=GRAIN_COLUMNS, columns="metric_code", values="metric_value_keur")
    counts = grouped.pivot(index=GRAIN_COLUMNS, columns="metric_code", values="record_count")
    files = grouped.pivot(index=GRAIN_COLUMNS, columns="metric_code", values="source_files")
    rows = grouped.pivot(index=GRAIN_COLUMNS, columns="metric_code", values="source_rows")

    values = values.rename(columns={"GSV": "gsv_keur", "TURNOVER": "turnover_keur"})
    counts = counts.rename(columns={"GSV": "gsv_record_count", "TURNOVER": "turnover_record_count"})
    files = files.rename(columns={"GSV": "gsv_source_files", "TURNOVER": "turnover_source_files"})
    rows = rows.rename(columns={"GSV": "gsv_source_rows", "TURNOVER": "turnover_source_rows"})

    wide = values.join(counts, how="outer").join(files, how="outer").join(rows, how="outer").reset_index()
    for column in ["gsv_record_count", "turnover_record_count"]:
        if column not in wide:
            wide[column] = 0
        wide[column] = wide[column].fillna(0).astype(int)
    for column in ["gsv_source_files", "turnover_source_files", "gsv_source_rows", "turnover_source_rows"]:
        if column not in wide:
            wide[column] = ""
        wide[column] = wide[column].fillna("")
    return wide


def _quality_flags(row: pd.Series) -> str:
    flags: list[str] = []
    if row["gsv_record_count"] == 0:
        flags.append("GSV_MISSING")
    elif row["gsv_record_count"] > 1:
        flags.append("GSV_DUPLICATE")
    if row["turnover_record_count"] == 0:
        flags.append("TURNOVER_MISSING")
    elif row["turnover_record_count"] > 1:
        flags.append("TURNOVER_DUPLICATE")
    if pd.notna(row["gsv_keur"]) and float(row["gsv_keur"]) < 0:
        flags.append("GSV_NEGATIVE")
    if pd.notna(row["turnover_keur"]) and float(row["turnover_keur"]) < 0:
        flags.append("TURNOVER_NEGATIVE")
    if (
        pd.notna(row["gsv_keur"])
        and pd.notna(row["turnover_keur"])
        and float(row["turnover_keur"]) > float(row["gsv_keur"])
    ):
        flags.append("TURNOVER_GT_GSV")
    if pd.isna(row["customer_name"]):
        flags.append("CUSTOMER_MAPPING_MISSING")
    if pd.isna(row["brand_name"]):
        flags.append("BRAND_MAPPING_MISSING")
    if pd.isna(row["product_name"]):
        flags.append("PRODUCT_MAPPING_MISSING")
    if bool(row.get("mapping_review_required", False)):
        flags.append("PRODUCT_MAPPING_REVIEW")
    return ";".join(flags) if flags else "OK"


def build_sales_master(
    project_root: Path,
    *,
    output_path: Path | None = None,
) -> dict[str, Any]:
    paths = ProjectPaths.from_root(project_root)
    settings = load_json(paths.settings_file)
    raw_sales, sales_sources = load_sales(paths, settings)
    invalid_sources = [source.path for source in sales_sources if source.schema_status != "PASS"]
    if invalid_sources:
        raise ValueError(f"Sales files with invalid schema: {invalid_sources}")

    customers, brands, products, _ = load_mappings(paths)
    master = _metric_wide(raw_sales)
    master = master.merge(customers, on="customer_code", how="left", validate="many_to_one")
    master = master.merge(brands, on="brand_code", how="left", validate="many_to_one")
    master = master.merge(
        products[
            [
                "product_key",
                "product_name",
                "product_group_lv1",
                "product_group_lv2",
                "mapping_review_required",
            ]
        ],
        on="product_key",
        how="left",
        validate="many_to_one",
    )

    master["reporting_year"] = master["reporting_month"].dt.year.astype("Int64")
    master["month_number"] = master["reporting_month"].dt.month.astype("Int64")
    master["discount_keur"] = master["gsv_keur"] - master["turnover_keur"]
    master["discount_pct_to"] = master["discount_keur"] / master["turnover_keur"].replace(0, np.nan)
    master["discount_pct_gsv"] = master["discount_keur"] / master["gsv_keur"].replace(0, np.nan)
    master["mapping_review_required"] = master["mapping_review_required"].fillna(False).astype(bool)
    master["data_quality_flags"] = master.apply(_quality_flags, axis=1)
    blocking_pattern = (
        r"GSV_MISSING|TURNOVER_MISSING|GSV_DUPLICATE|TURNOVER_DUPLICATE|TURNOVER_GT_GSV|"
        r"CUSTOMER_MAPPING_MISSING|BRAND_MAPPING_MISSING|PRODUCT_MAPPING_MISSING"
    )
    master["certified_for_analysis"] = ~master["data_quality_flags"].str.contains(
        blocking_pattern, regex=True
    )
    master["data_quality_status"] = np.select(
        [
            master["certified_for_analysis"] & master["data_quality_flags"].eq("OK"),
            master["certified_for_analysis"],
        ],
        ["VALID", "REVIEW"],
        default="INVALID",
    )

    columns = [
        "reporting_month",
        "reporting_year",
        "month_number",
        "customer_code",
        "customer_name",
        "channel_code",
        "brand_code",
        "brand_name",
        "product_key",
        "product_name",
        "pack_type",
        "pack_size",
        "product_group_lv1",
        "product_group_lv2",
        "gsv_keur",
        "turnover_keur",
        "discount_keur",
        "discount_pct_to",
        "discount_pct_gsv",
        "gsv_record_count",
        "turnover_record_count",
        "mapping_review_required",
        "certified_for_analysis",
        "data_quality_status",
        "data_quality_flags",
        "gsv_source_files",
        "gsv_source_rows",
        "turnover_source_files",
        "turnover_source_rows",
    ]
    master = master[columns].sort_values(
        ["reporting_month", "customer_code", "brand_code", "product_key"],
        kind="stable",
    )
    master["reporting_month"] = master["reporting_month"].dt.strftime("%Y-%m-%d")

    target = (output_path or paths.output_dir / settings["outputs"]["sales_master"]).resolve()
    protected = {paths.pnl_file.resolve(), paths.market_file.resolve(), paths.mapping_file.resolve()}
    if target in protected or target.parent == paths.sales_dir.resolve():
        raise ValueError("The Sales master output cannot overwrite a governed input file.")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    master.to_csv(temporary, index=False, encoding="utf-8")
    temporary.replace(target)

    return {
        "output_path": target.as_posix(),
        "source_file_count": len(sales_sources),
        "source_record_count": int(len(raw_sales)),
        "master_row_count": int(len(master)),
        "certified_row_count": int(master["certified_for_analysis"].sum()),
        "review_row_count": int((master["data_quality_status"] == "REVIEW").sum()),
        "invalid_row_count": int((master["data_quality_status"] == "INVALID").sum()),
    }

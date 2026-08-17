"""Calculate the metrics defined in STORYLINE_METRIC_FRAMEWORK.md.

Aggregated Sales metrics compare the two latest consecutive full calendar
years. Monthly Sales metrics retain aligned current/prior-year observations for
volatility analysis. P&L and Market metrics remain standalone because their
grains and reporting periods differ from the Sales master.
"""

from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SALES_PATH = PROJECT_ROOT / "outputs" / "sales_master.csv"
PNL_PATH = PROJECT_ROOT / "inputs" / "pnl" / "P&L Table.xlsx"
MARKET_PATH = PROJECT_ROOT / "inputs" / "market" / "Market Report MAT Nov'24.xlsx"


# ---------------------------------------------------------------------------
# 3.1 Sales filter and comparison years
# ---------------------------------------------------------------------------

sales_df = pd.read_csv(
    SALES_PATH,
    dtype={"customer_code": "string", "brand_code": "string"},
    parse_dates=["reporting_month"],
)

certified_sales_df = sales_df.loc[sales_df["certified_for_analysis"].eq(True)].copy()

_months_by_year = (
    certified_sales_df.assign(
        reporting_year=certified_sales_df["reporting_month"].dt.year,
        month_number=certified_sales_df["reporting_month"].dt.month,
    )
    .groupby("reporting_year")["month_number"]
    .agg(lambda values: frozenset(values.unique()))
)
COMPLETE_YEARS = tuple(
    int(year)
    for year, months in _months_by_year.items()
    if months == frozenset(range(1, 13))
)
_consecutive_year_pairs = [
    (prior_year, current_year)
    for prior_year, current_year in zip(COMPLETE_YEARS, COMPLETE_YEARS[1:])
    if current_year == prior_year + 1
]
if not _consecutive_year_pairs:
    raise ValueError(
        "Sales metrics require at least two consecutive calendar years with "
        "certified data in all 12 months."
    )

PRIOR_YEAR, CURRENT_YEAR = _consecutive_year_pairs[-1]


def _series_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divide two Series, returning NaN when the denominator is zero."""
    return numerator.div(denominator.replace(0, np.nan))


def _scalar_ratio(numerator: float, denominator: float) -> float:
    """Divide two scalar values, returning NaN when the denominator is zero."""
    if pd.isna(denominator) or denominator == 0:
        return np.nan
    return numerator / denominator


def _year_aggregate(
    data: pd.DataFrame,
    group_cols: Sequence[str],
    value_cols: Sequence[str],
) -> pd.DataFrame:
    """Aggregate current and prior Sales years and outer-join their entities."""

    def aggregate_one_year(year: int, prefix: str) -> pd.DataFrame:
        period_data = data.loc[data["reporting_month"].dt.year.eq(year)]
        renamed = {column: f"{prefix}_{column}" for column in value_cols}

        if group_cols:
            return (
                period_data.groupby(list(group_cols), dropna=False, as_index=False)[
                    list(value_cols)
                ]
                .sum()
                .rename(columns=renamed)
            )

        totals = {
            f"{prefix}_{column}": [period_data[column].sum()] for column in value_cols
        }
        return pd.DataFrame(totals)

    current = aggregate_one_year(CURRENT_YEAR, "current")
    prior = aggregate_one_year(PRIOR_YEAR, "prior")

    if group_cols:
        result = current.merge(prior, on=list(group_cols), how="outer")
    else:
        result = pd.concat([current, prior], axis=1)

    measure_cols = [
        f"{prefix}_{column}" for prefix in ("current", "prior") for column in value_cols
    ]
    result[measure_cols] = result[measure_cols].fillna(0.0)
    return result


def _joined_label(frame: pd.DataFrame, columns: Sequence[str]) -> pd.Series:
    """Join identifier or name columns into one readable entity label."""
    return (
        frame[list(columns)]
        .astype("string")
        .fillna("<missing>")
        .agg(" | ".join, axis=1)
    )


def _add_entity_columns(
    frame: pd.DataFrame,
    dimension: str,
    id_cols: Sequence[str],
    name_cols: Sequence[str],
) -> pd.DataFrame:
    """Normalize differently-grained results into a stackable entity schema."""
    result = frame.copy()
    result.insert(0, "dimension", dimension)

    if id_cols:
        result.insert(1, "entity_key", _joined_label(result, id_cols))
        result.insert(2, "entity_name", _joined_label(result, name_cols or id_cols))
    else:
        result.insert(1, "entity_key", "TOTAL")
        result.insert(2, "entity_name", "Total")

    return result


SALES_DIMENSIONS = (
    ("Total", (), (), ()),
    ("Brand", ("brand_code", "brand_name"), ("brand_code",), ("brand_name",)),
    ("Channel", ("channel_code",), ("channel_code",), ("channel_code",)),
    (
        "Customer",
        ("customer_code", "customer_name"),
        ("customer_code",),
        ("customer_name",),
    ),
    (
        "Exact Product",
        ("product_key", "product_name"),
        ("product_key",),
        ("product_name",),
    ),
    ("Pack Type", ("pack_type",), ("pack_type",), ("pack_type",)),
    ("Pack Size", ("pack_size",), ("pack_size",), ("pack_size",)),
)


def _build_sales_value_metrics(value_col: str, metric_name: str) -> pd.DataFrame:
    """Build annual current, prior, change, and growth across Sales dimensions."""
    frames: list[pd.DataFrame] = []

    for dimension, group_cols, id_cols, name_cols in SALES_DIMENSIONS:
        result = _year_aggregate(certified_sales_df, group_cols, (value_col,))
        result = result.rename(
            columns={
                f"current_{value_col}": f"current_{metric_name}_keur",
                f"prior_{value_col}": f"prior_{metric_name}_keur",
            }
        )
        result[f"{metric_name}_change_keur"] = (
            result[f"current_{metric_name}_keur"] - result[f"prior_{metric_name}_keur"]
        )
        result[f"{metric_name}_growth_pct"] = (
            _series_ratio(
                result[f"current_{metric_name}_keur"],
                result[f"prior_{metric_name}_keur"],
            )
            - 1
        )
        result = _add_entity_columns(result, dimension, id_cols, name_cols)
        frames.append(result)

    output = pd.concat(frames, ignore_index=True)
    output.insert(0, "current_year", CURRENT_YEAR)
    output.insert(1, "prior_year", PRIOR_YEAR)

    measure_cols = [
        f"current_{metric_name}_keur",
        f"prior_{metric_name}_keur",
        f"{metric_name}_change_keur",
        f"{metric_name}_growth_pct",
    ]
    return output[
        [
            "current_year",
            "prior_year",
            "dimension",
            "entity_key",
            "entity_name",
            *measure_cols,
        ]
    ]


# ---------------------------------------------------------------------------
# 3.3 Turnover
# ---------------------------------------------------------------------------

turnover_metrics_df = _build_sales_value_metrics("turnover_keur", "to")


# ---------------------------------------------------------------------------
# 3.4 Gross Sales Value
# ---------------------------------------------------------------------------

gsv_metrics_df = _build_sales_value_metrics("gsv_keur", "gsv")


# ---------------------------------------------------------------------------
# 3.5 Driver contribution
# ---------------------------------------------------------------------------

_total_to_change = turnover_metrics_df.loc[
    turnover_metrics_df["dimension"].eq("Total"), "to_change_keur"
].iat[0]

driver_contribution_df = turnover_metrics_df.loc[
    turnover_metrics_df["dimension"].isin(
        ["Brand", "Channel", "Customer", "Exact Product"]
    )
].copy()
driver_contribution_df.insert(
    driver_contribution_df.columns.get_loc("to_change_keur") + 1,
    "total_to_change_keur",
    _total_to_change,
)
driver_contribution_df["change_contribution_pct"] = (
    _scalar_ratio(1.0, _total_to_change) * driver_contribution_df["to_change_keur"]
)


# ---------------------------------------------------------------------------
# 3.6 Product and Pack mix
# ---------------------------------------------------------------------------

MIX_DIMENSIONS = (
    ("Pack Type", ("pack_type",), (), ("pack_type",), ("pack_type",)),
    ("Pack Size", ("pack_size",), (), ("pack_size",), ("pack_size",)),
    (
        "Exact Product",
        ("product_key", "product_name"),
        (),
        ("product_key",),
        ("product_name",),
    ),
    (
        "Brand × Product",
        ("brand_code", "brand_name", "product_key", "product_name"),
        ("brand_code", "brand_name"),
        ("brand_code", "product_key"),
        ("brand_name", "product_name"),
    ),
    (
        "Channel × Product",
        ("channel_code", "product_key", "product_name"),
        ("channel_code",),
        ("channel_code", "product_key"),
        ("channel_code", "product_name"),
    ),
)


def _build_mix_metrics() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for dimension, group_cols, parent_cols, id_cols, name_cols in MIX_DIMENSIONS:
        result = _year_aggregate(certified_sales_df, group_cols, ("turnover_keur",))
        result = result.rename(
            columns={
                "current_turnover_keur": "current_to_keur",
                "prior_turnover_keur": "prior_to_keur",
            }
        )

        if parent_cols:
            denominators = _year_aggregate(
                certified_sales_df, parent_cols, ("turnover_keur",)
            ).rename(
                columns={
                    "current_turnover_keur": "current_mix_denominator_to_keur",
                    "prior_turnover_keur": "prior_mix_denominator_to_keur",
                }
            )
            result = result.merge(denominators, on=list(parent_cols), how="left")
        else:
            total_denominators = _year_aggregate(
                certified_sales_df, (), ("turnover_keur",)
            )
            result["current_mix_denominator_to_keur"] = total_denominators[
                "current_turnover_keur"
            ].iat[0]
            result["prior_mix_denominator_to_keur"] = total_denominators[
                "prior_turnover_keur"
            ].iat[0]

        result["to_change_keur"] = result["current_to_keur"] - result["prior_to_keur"]
        result["to_growth_pct"] = (
            _series_ratio(result["current_to_keur"], result["prior_to_keur"]) - 1
        )
        result["current_to_mix_pct"] = _series_ratio(
            result["current_to_keur"], result["current_mix_denominator_to_keur"]
        )
        result["prior_to_mix_pct"] = _series_ratio(
            result["prior_to_keur"], result["prior_mix_denominator_to_keur"]
        )
        result["mix_movement_pp"] = (
            result["current_to_mix_pct"] - result["prior_to_mix_pct"]
        ) * 100

        result = _add_entity_columns(result, dimension, id_cols, name_cols)
        if parent_cols:
            parent_id_cols = (
                tuple(
                    column
                    for column in parent_cols
                    if column.endswith("_code") or column.endswith("_key")
                )
                or parent_cols
            )
            parent_name_cols = (
                tuple(column for column in parent_cols if column.endswith("_name"))
                or parent_id_cols
            )
            result.insert(3, "mix_scope_key", _joined_label(result, parent_id_cols))
            result.insert(4, "mix_scope_name", _joined_label(result, parent_name_cols))
        else:
            result.insert(3, "mix_scope_key", "TOTAL")
            result.insert(4, "mix_scope_name", "Total")

        frames.append(result)

    output = pd.concat(frames, ignore_index=True)
    output.insert(0, "current_year", CURRENT_YEAR)
    output.insert(1, "prior_year", PRIOR_YEAR)
    return output[
        [
            "current_year",
            "prior_year",
            "dimension",
            "entity_key",
            "entity_name",
            "mix_scope_key",
            "mix_scope_name",
            "current_to_keur",
            "prior_to_keur",
            "to_change_keur",
            "to_growth_pct",
            "current_to_mix_pct",
            "prior_to_mix_pct",
            "mix_movement_pp",
        ]
    ]


product_pack_mix_df = _build_mix_metrics()


# ---------------------------------------------------------------------------
# 3.7 Active customer and customer penetration
# ---------------------------------------------------------------------------

PENETRATION_DIMENSIONS = (
    (
        "Exact Product",
        ("product_key", "product_name"),
        ("product_key",),
        ("product_name",),
    ),
    (
        "Brand × Product",
        ("brand_code", "brand_name", "product_key", "product_name"),
        ("brand_code", "product_key"),
        ("brand_name", "product_name"),
    ),
    (
        "Channel × Product",
        ("channel_code", "product_key", "product_name"),
        ("channel_code", "product_key"),
        ("channel_code", "product_name"),
    ),
)


def _total_active_customers(data: pd.DataFrame, year: int) -> int:
    customer_to = (
        data.loc[data["reporting_month"].dt.year.eq(year)]
        .groupby("customer_code", dropna=False)["turnover_keur"]
        .sum()
    )
    return int(customer_to.gt(0).sum())


def _active_customer_count(
    data: pd.DataFrame,
    year: int,
    group_cols: Sequence[str],
    output_col: str,
) -> pd.DataFrame:
    customer_product_to = (
        data.loc[data["reporting_month"].dt.year.eq(year)]
        .groupby([*group_cols, "customer_code"], dropna=False, as_index=False)[
            "turnover_keur"
        ]
        .sum()
    )
    return (
        customer_product_to.loc[customer_product_to["turnover_keur"].gt(0)]
        .groupby(list(group_cols), dropna=False, as_index=False)["customer_code"]
        .nunique()
        .rename(columns={"customer_code": output_col})
    )


def _build_customer_penetration_metrics() -> pd.DataFrame:
    current_total_active = _total_active_customers(certified_sales_df, CURRENT_YEAR)
    prior_total_active = _total_active_customers(certified_sales_df, PRIOR_YEAR)
    frames: list[pd.DataFrame] = []

    for dimension, group_cols, id_cols, name_cols in PENETRATION_DIMENSIONS:
        current = _active_customer_count(
            certified_sales_df,
            CURRENT_YEAR,
            group_cols,
            "current_product_active_customers",
        )
        prior = _active_customer_count(
            certified_sales_df,
            PRIOR_YEAR,
            group_cols,
            "prior_product_active_customers",
        )
        result = current.merge(prior, on=list(group_cols), how="outer")
        count_cols = [
            "current_product_active_customers",
            "prior_product_active_customers",
        ]
        result[count_cols] = result[count_cols].fillna(0).astype("int64")
        result["active_customer_change"] = (
            result["current_product_active_customers"]
            - result["prior_product_active_customers"]
        )
        result["current_total_active_customers"] = current_total_active
        result["prior_total_active_customers"] = prior_total_active
        result["current_customer_penetration_pct"] = _series_ratio(
            result["current_product_active_customers"],
            result["current_total_active_customers"],
        )
        result["prior_customer_penetration_pct"] = _series_ratio(
            result["prior_product_active_customers"],
            result["prior_total_active_customers"],
        )
        result["customer_penetration_movement_pp"] = (
            result["current_customer_penetration_pct"]
            - result["prior_customer_penetration_pct"]
        ) * 100
        result = _add_entity_columns(result, dimension, id_cols, name_cols)
        frames.append(result)

    output = pd.concat(frames, ignore_index=True)
    output.insert(0, "current_year", CURRENT_YEAR)
    output.insert(1, "prior_year", PRIOR_YEAR)
    return output[
        [
            "current_year",
            "prior_year",
            "dimension",
            "entity_key",
            "entity_name",
            "current_product_active_customers",
            "prior_product_active_customers",
            "active_customer_change",
            "current_total_active_customers",
            "prior_total_active_customers",
            "current_customer_penetration_pct",
            "prior_customer_penetration_pct",
            "customer_penetration_movement_pp",
        ]
    ]


customer_penetration_df = _build_customer_penetration_metrics()


# ---------------------------------------------------------------------------
# 3.8 Discount and Gross-to-Net
# ---------------------------------------------------------------------------

DISCOUNT_DIMENSIONS = SALES_DIMENSIONS[:5]


def _build_discount_metrics() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    value_cols = ("gsv_keur", "turnover_keur", "discount_keur")

    for dimension, group_cols, id_cols, name_cols in DISCOUNT_DIMENSIONS:
        result = _year_aggregate(certified_sales_df, group_cols, value_cols)
        result = result.rename(
            columns={
                "current_turnover_keur": "current_to_keur",
                "prior_turnover_keur": "prior_to_keur",
            }
        )
        result["discount_change_keur"] = (
            result["current_discount_keur"] - result["prior_discount_keur"]
        )
        result["current_discount_pct_to"] = _series_ratio(
            result["current_discount_keur"], result["current_to_keur"]
        )
        result["prior_discount_pct_to"] = _series_ratio(
            result["prior_discount_keur"], result["prior_to_keur"]
        )
        result["discount_pct_to_movement_bps"] = (
            result["current_discount_pct_to"] - result["prior_discount_pct_to"]
        ) * 10_000
        result["current_discount_pct_gsv"] = _series_ratio(
            result["current_discount_keur"], result["current_gsv_keur"]
        )
        result["prior_discount_pct_gsv"] = _series_ratio(
            result["prior_discount_keur"], result["prior_gsv_keur"]
        )
        result["discount_pct_gsv_movement_bps"] = (
            result["current_discount_pct_gsv"] - result["prior_discount_pct_gsv"]
        ) * 10_000
        result = _add_entity_columns(result, dimension, id_cols, name_cols)
        frames.append(result)

    output = pd.concat(frames, ignore_index=True)
    output.insert(0, "current_year", CURRENT_YEAR)
    output.insert(1, "prior_year", PRIOR_YEAR)
    return output[
        [
            "current_year",
            "prior_year",
            "dimension",
            "entity_key",
            "entity_name",
            "current_gsv_keur",
            "prior_gsv_keur",
            "current_to_keur",
            "prior_to_keur",
            "current_discount_keur",
            "prior_discount_keur",
            "discount_change_keur",
            "current_discount_pct_to",
            "prior_discount_pct_to",
            "discount_pct_to_movement_bps",
            "current_discount_pct_gsv",
            "prior_discount_pct_gsv",
            "discount_pct_gsv_movement_bps",
        ]
    ]


discount_metrics_df = _build_discount_metrics()


# ---------------------------------------------------------------------------
# 3.9 Monthly comparable Sales metrics for volatility
# ---------------------------------------------------------------------------

VOLATILITY_DIMENSIONS = SALES_DIMENSIONS[:3]
VOLATILITY_VALUE_COLS = ("turnover_keur", "gsv_keur", "discount_keur")


def _monthly_dimension_values(
    data: pd.DataFrame,
    year: int,
    month_number: int,
    group_cols: Sequence[str],
    entities: pd.DataFrame,
    prefix: str,
) -> pd.DataFrame:
    """Aggregate one month while retaining the full two-year entity universe."""
    month_data = data.loc[
        data["reporting_month"].dt.year.eq(year)
        & data["reporting_month"].dt.month.eq(month_number)
    ]

    value_renames = {column: f"{prefix}_{column}" for column in VOLATILITY_VALUE_COLS}
    active_col = f"{prefix}_active_customers"

    if group_cols:
        values = (
            month_data.groupby(list(group_cols), dropna=False, as_index=False)[
                list(VOLATILITY_VALUE_COLS)
            ]
            .sum()
            .rename(columns=value_renames)
        )
        customer_to = month_data.groupby(
            [*group_cols, "customer_code"], dropna=False, as_index=False
        )["turnover_keur"].sum()
        active = (
            customer_to.loc[customer_to["turnover_keur"].gt(0)]
            .groupby(list(group_cols), dropna=False, as_index=False)["customer_code"]
            .nunique()
            .rename(columns={"customer_code": active_col})
        )
        result = entities.merge(values, on=list(group_cols), how="left")
        result = result.merge(active, on=list(group_cols), how="left")
    else:
        customer_to = month_data.groupby("customer_code", dropna=False)[
            "turnover_keur"
        ].sum()
        result = pd.DataFrame(
            {
                **{
                    f"{prefix}_{column}": [month_data[column].sum()]
                    for column in VOLATILITY_VALUE_COLS
                },
                active_col: [int(customer_to.gt(0).sum())],
            }
        )

    measure_cols = [*value_renames.values(), active_col]
    result[measure_cols] = result[measure_cols].fillna(0.0)
    result[active_col] = result[active_col].astype("int64")
    return result


def _build_sales_volatility_metrics() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    analysis_years = certified_sales_df.loc[
        certified_sales_df["reporting_month"].dt.year.isin([PRIOR_YEAR, CURRENT_YEAR])
    ]

    for dimension, group_cols, id_cols, name_cols in VOLATILITY_DIMENSIONS:
        if group_cols:
            entities = analysis_years[list(group_cols)].drop_duplicates()
        else:
            entities = pd.DataFrame(index=[0])

        for month_number in range(1, 13):
            current = _monthly_dimension_values(
                certified_sales_df,
                CURRENT_YEAR,
                month_number,
                group_cols,
                entities,
                "current",
            )
            prior = _monthly_dimension_values(
                certified_sales_df,
                PRIOR_YEAR,
                month_number,
                group_cols,
                entities,
                "prior",
            )
            if group_cols:
                result = current.merge(prior, on=list(group_cols), how="outer")
            else:
                result = pd.concat([current, prior], axis=1)

            result["to_change_keur"] = (
                result["current_turnover_keur"] - result["prior_turnover_keur"]
            )
            result["to_growth_pct"] = (
                _series_ratio(
                    result["current_turnover_keur"],
                    result["prior_turnover_keur"],
                )
                - 1
            )
            result["gsv_change_keur"] = (
                result["current_gsv_keur"] - result["prior_gsv_keur"]
            )
            result["gsv_growth_pct"] = (
                _series_ratio(result["current_gsv_keur"], result["prior_gsv_keur"]) - 1
            )
            result["discount_change_keur"] = (
                result["current_discount_keur"] - result["prior_discount_keur"]
            )
            result["current_discount_pct_to"] = _series_ratio(
                result["current_discount_keur"], result["current_turnover_keur"]
            )
            result["prior_discount_pct_to"] = _series_ratio(
                result["prior_discount_keur"], result["prior_turnover_keur"]
            )
            result["discount_pct_to_movement_bps"] = (
                result["current_discount_pct_to"] - result["prior_discount_pct_to"]
            ) * 10_000
            result["current_discount_pct_gsv"] = _series_ratio(
                result["current_discount_keur"], result["current_gsv_keur"]
            )
            result["prior_discount_pct_gsv"] = _series_ratio(
                result["prior_discount_keur"], result["prior_gsv_keur"]
            )
            result["discount_pct_gsv_movement_bps"] = (
                result["current_discount_pct_gsv"] - result["prior_discount_pct_gsv"]
            ) * 10_000
            result["active_customers_change"] = (
                result["current_active_customers"] - result["prior_active_customers"]
            )

            result = _add_entity_columns(result, dimension, id_cols, name_cols)
            result.insert(0, "month_number", month_number)
            result.insert(
                1,
                "current_month",
                pd.Timestamp(CURRENT_YEAR, month_number, 1),
            )
            result.insert(
                2,
                "prior_month",
                pd.Timestamp(PRIOR_YEAR, month_number, 1),
            )
            frames.append(result)

    output = pd.concat(frames, ignore_index=True)
    output.insert(0, "current_year", CURRENT_YEAR)
    output.insert(1, "prior_year", PRIOR_YEAR)
    return output[
        [
            "current_year",
            "prior_year",
            "month_number",
            "current_month",
            "prior_month",
            "dimension",
            "entity_key",
            "entity_name",
            "current_turnover_keur",
            "prior_turnover_keur",
            "to_change_keur",
            "to_growth_pct",
            "current_gsv_keur",
            "prior_gsv_keur",
            "gsv_change_keur",
            "gsv_growth_pct",
            "current_discount_keur",
            "prior_discount_keur",
            "discount_change_keur",
            "current_discount_pct_to",
            "prior_discount_pct_to",
            "discount_pct_to_movement_bps",
            "current_discount_pct_gsv",
            "prior_discount_pct_gsv",
            "discount_pct_gsv_movement_bps",
            "current_active_customers",
            "prior_active_customers",
            "active_customers_change",
        ]
    ]


sales_volatility_df = _build_sales_volatility_metrics()


# ---------------------------------------------------------------------------
# 4.1 P&L metrics (standalone Brand/Total x Year source)
# ---------------------------------------------------------------------------


def _build_pnl_metrics() -> pd.DataFrame:
    # Only the first (EUR) block is used; the VND block is a currency conversion
    # of the same P&L and would duplicate the underlying economics.
    raw = pd.read_excel(
        PNL_PATH,
        sheet_name="PnL table",
        header=None,
        usecols="A:M",
        nrows=15,
        engine="openpyxl",
    )
    metric_rows = {
        str(label).strip(): row_index
        for row_index, label in raw.iloc[:, 0].items()
        if pd.notna(label)
    }

    source_labels = {
        "gsv": "Gross Sales Value (GSV)",
        "discount": "Discount",
        "turnover": "Turnover (TO)",
        "supply_chain_cost": "Total Supply Chain Cost",
        "marketing_expense": "Marketing Expense",
    }
    missing_labels = set(source_labels.values()).difference(metric_rows)
    if missing_labels:
        raise ValueError(f"Missing expected P&L rows: {sorted(missing_labels)}")

    records: list[dict[str, object]] = []
    for prior_col in range(1, 13, 3):
        brand = raw.iat[0, prior_col]
        if pd.isna(brand):
            continue

        current_col = prior_col + 1
        prior_year = int(raw.iat[1, prior_col])
        current_year = int(raw.iat[1, current_col])

        def source_value(metric: str, column: int) -> float:
            value = raw.iat[metric_rows[source_labels[metric]], column]
            return float(value)

        prior_gsv = source_value("gsv", prior_col)
        current_gsv = source_value("gsv", current_col)
        prior_discount = source_value("discount", prior_col)
        current_discount = source_value("discount", current_col)
        prior_to = source_value("turnover", prior_col)
        current_to = source_value("turnover", current_col)
        prior_supply_chain = source_value("supply_chain_cost", prior_col)
        current_supply_chain = source_value("supply_chain_cost", current_col)
        prior_marketing = source_value("marketing_expense", prior_col)
        current_marketing = source_value("marketing_expense", current_col)

        prior_gross_profit = prior_to - prior_supply_chain
        current_gross_profit = current_to - current_supply_chain
        prior_gross_margin = _scalar_ratio(prior_gross_profit, prior_to)
        current_gross_margin = _scalar_ratio(current_gross_profit, current_to)
        prior_pbo = prior_gross_profit - prior_marketing
        current_pbo = current_gross_profit - current_marketing
        prior_pbo_margin = _scalar_ratio(prior_pbo, prior_to)
        current_pbo_margin = _scalar_ratio(current_pbo, current_to)
        gross_profit_change = current_gross_profit - prior_gross_profit
        marketing_change = current_marketing - prior_marketing
        pbo_change = current_pbo - prior_pbo
        pbo_change_from_bridge = gross_profit_change - marketing_change

        records.append(
            {
                "brand": str(brand).strip(),
                "current_year": current_year,
                "prior_year": prior_year,
                "current_gsv_eur": current_gsv,
                "prior_gsv_eur": prior_gsv,
                "gsv_growth_pct": _scalar_ratio(current_gsv, prior_gsv) - 1,
                "current_discount_eur": current_discount,
                "prior_discount_eur": prior_discount,
                "discount_change_eur": current_discount - prior_discount,
                "current_turnover_eur": current_to,
                "prior_turnover_eur": prior_to,
                "turnover_growth_pct": _scalar_ratio(current_to, prior_to) - 1,
                "current_supply_chain_cost_eur": current_supply_chain,
                "prior_supply_chain_cost_eur": prior_supply_chain,
                "supply_chain_cost_change_eur": (
                    current_supply_chain - prior_supply_chain
                ),
                "current_gross_profit_eur": current_gross_profit,
                "prior_gross_profit_eur": prior_gross_profit,
                "gross_profit_change_eur": gross_profit_change,
                "current_gross_margin_pct": current_gross_margin,
                "prior_gross_margin_pct": prior_gross_margin,
                "gross_margin_movement_bps": (current_gross_margin - prior_gross_margin)
                * 10_000,
                "current_marketing_expense_eur": current_marketing,
                "prior_marketing_expense_eur": prior_marketing,
                "marketing_expense_change_eur": marketing_change,
                "current_pbo_eur": current_pbo,
                "prior_pbo_eur": prior_pbo,
                "pbo_change_eur": pbo_change,
                "current_pbo_margin_pct": current_pbo_margin,
                "prior_pbo_margin_pct": prior_pbo_margin,
                "pbo_margin_movement_bps": (current_pbo_margin - prior_pbo_margin)
                * 10_000,
                "pbo_change_from_bridge_eur": pbo_change_from_bridge,
                "pbo_bridge_check_eur": pbo_change - pbo_change_from_bridge,
            }
        )

    return pd.DataFrame.from_records(records)


pnl_metrics_df = _build_pnl_metrics()


# ---------------------------------------------------------------------------
# 5.1 Market metrics (standalone MAT source)
# ---------------------------------------------------------------------------


def _build_market_metrics() -> pd.DataFrame:
    columns = [
        "channel",
        "segment",
        "manufacturer",
        "brand",
        "sales_value_mat_1_meur",
        "sales_value_mat_meur",
        "source_sales_value_gain_loss_meur",
        "value_share_mat_1_pct",
        "value_share_mat_pct",
        "source_share_gain_loss_pp",
    ]
    result = pd.read_excel(
        MARKET_PATH,
        sheet_name="Market Data",
        header=None,
        skiprows=4,
        usecols="B:K",
        names=columns,
        engine="openpyxl",
    ).dropna(how="all")

    for column in ("channel", "segment", "manufacturer", "brand"):
        result[column] = result[column].astype("string").str.strip()

    result.insert(0, "mat_period", MARKET_PATH.stem.removeprefix("Market Report "))
    result["market_value_growth_pct"] = (
        _series_ratio(result["sales_value_mat_meur"], result["sales_value_mat_1_meur"])
        - 1
    )
    result["sales_value_movement_meur"] = (
        result["sales_value_mat_meur"] - result["sales_value_mat_1_meur"]
    )
    result["share_movement_pp"] = (
        result["value_share_mat_pct"] - result["value_share_mat_1_pct"]
    )
    result["sales_value_gain_loss_check_meur"] = (
        result["sales_value_movement_meur"]
        - result["source_sales_value_gain_loss_meur"]
    )
    result["share_gain_loss_check_pp"] = (
        result["share_movement_pp"] - result["source_share_gain_loss_pp"]
    )

    sales_check = pd.Series(pd.NA, index=result.index, dtype="boolean")
    has_sales_check = result["source_sales_value_gain_loss_meur"].notna()
    sales_check.loc[has_sales_check] = np.isclose(
        result.loc[has_sales_check, "sales_value_gain_loss_check_meur"],
        0,
        atol=1e-9,
    )
    result["sales_value_gain_loss_matches_source"] = sales_check

    share_check = pd.Series(pd.NA, index=result.index, dtype="boolean")
    has_share_check = result["source_share_gain_loss_pp"].notna()
    share_check.loc[has_share_check] = np.isclose(
        result.loc[has_share_check, "share_gain_loss_check_pp"],
        0,
        atol=1e-9,
    )
    result["share_gain_loss_matches_source"] = share_check

    return result[
        [
            "mat_period",
            "channel",
            "segment",
            "manufacturer",
            "brand",
            "sales_value_mat_1_meur",
            "sales_value_mat_meur",
            "market_value_growth_pct",
            "sales_value_movement_meur",
            "source_sales_value_gain_loss_meur",
            "sales_value_gain_loss_check_meur",
            "sales_value_gain_loss_matches_source",
            "value_share_mat_1_pct",
            "value_share_mat_pct",
            "share_movement_pp",
            "source_share_gain_loss_pp",
            "share_gain_loss_check_pp",
            "share_gain_loss_matches_source",
        ]
    ]


market_metrics_df = _build_market_metrics()


# One discoverable registry while retaining a separate DataFrame per section.
METRIC_DATAFRAMES = {
    "turnover": turnover_metrics_df,
    "gsv": gsv_metrics_df,
    "driver_contribution": driver_contribution_df,
    "product_pack_mix": product_pack_mix_df,
    "customer_penetration": customer_penetration_df,
    "discount_gross_to_net": discount_metrics_df,
    "sales_volatility": sales_volatility_df,
    "pnl": pnl_metrics_df,
    "market": market_metrics_df,
}


if __name__ == "__main__":
    print(f"Sales comparison: FY{CURRENT_YEAR} vs FY{PRIOR_YEAR}")
    for dataframe_name, dataframe in METRIC_DATAFRAMES.items():
        print(
            f"{dataframe_name}: "
            f"{len(dataframe):,} rows x {len(dataframe.columns)} columns"
        )

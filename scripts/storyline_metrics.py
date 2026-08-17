"""Raw/P&L-aligned metrics used by the UniSweet report visuals.

The narrative reporting base deliberately includes every row in the Sales
master so Gross Sales Value, Discount and Turnover reconcile exactly to the
P&L workbook.  The existing ``scripts/metrics.py`` remains the separate
certified-data analytical view.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SALES_PATH = PROJECT_ROOT / "outputs" / "sales_master.csv"
PNL_PATH = PROJECT_ROOT / "inputs" / "pnl" / "P&L Table.xlsx"
MARKET_PATH = PROJECT_ROOT / "inputs" / "market" / "Market Report MAT Nov'24.xlsx"

PRIOR_YEAR = 2023
CURRENT_YEAR = 2024


def _ratio(numerator: pd.Series | float, denominator: pd.Series | float):
    """Divide while returning NaN for zero denominators."""
    if isinstance(denominator, pd.Series):
        return numerator / denominator.replace(0, np.nan)
    if pd.isna(denominator) or denominator == 0:
        return np.nan
    return numerator / denominator


def _annual_sales(
    sales: pd.DataFrame,
    group_cols: list[str],
) -> pd.DataFrame:
    """Return prior/current Sales values, changes, growth and discount rates."""
    value_cols = ["gsv_keur", "turnover_keur", "discount_keur"]
    if group_cols:
        grouped = (
            sales.groupby([*group_cols, "reporting_year"], dropna=False)[value_cols]
            .sum()
            .unstack("reporting_year", fill_value=0)
        )
        grouped.columns = [f"{metric}_{int(year)}" for metric, year in grouped.columns]
        result = grouped.reset_index()
    else:
        values: dict[str, list[float]] = {}
        for year in (PRIOR_YEAR, CURRENT_YEAR):
            period = sales.loc[sales["reporting_year"].eq(year), value_cols].sum()
            for metric in value_cols:
                values[f"{metric}_{year}"] = [float(period[metric])]
        result = pd.DataFrame(values)

    for metric in value_cols:
        for year in (PRIOR_YEAR, CURRENT_YEAR):
            column = f"{metric}_{year}"
            if column not in result:
                result[column] = 0.0

    result["gsv_change_keur"] = result[f"gsv_keur_{CURRENT_YEAR}"] - result[f"gsv_keur_{PRIOR_YEAR}"]
    result["to_change_keur"] = result[f"turnover_keur_{CURRENT_YEAR}"] - result[f"turnover_keur_{PRIOR_YEAR}"]
    result["discount_change_keur"] = result[f"discount_keur_{CURRENT_YEAR}"] - result[f"discount_keur_{PRIOR_YEAR}"]
    result["gsv_growth_pct"] = _ratio(result[f"gsv_keur_{CURRENT_YEAR}"], result[f"gsv_keur_{PRIOR_YEAR}"]) - 1
    result["to_growth_pct"] = _ratio(result[f"turnover_keur_{CURRENT_YEAR}"], result[f"turnover_keur_{PRIOR_YEAR}"]) - 1
    for year in (PRIOR_YEAR, CURRENT_YEAR):
        result[f"discount_pct_gsv_{year}"] = _ratio(
            result[f"discount_keur_{year}"], result[f"gsv_keur_{year}"]
        )
    result["discount_pct_gsv_movement_bps"] = (
        result[f"discount_pct_gsv_{CURRENT_YEAR}"]
        - result[f"discount_pct_gsv_{PRIOR_YEAR}"]
    ) * 10_000
    return result


def _load_sales() -> pd.DataFrame:
    sales = pd.read_csv(
        SALES_PATH,
        dtype={"customer_code": "string", "brand_code": "string"},
        parse_dates=["reporting_month"],
    )
    sales = sales.loc[sales["reporting_year"].isin([PRIOR_YEAR, CURRENT_YEAR])].copy()
    observed = set(sales["reporting_year"].dropna().astype(int).unique())
    if observed != {PRIOR_YEAR, CURRENT_YEAR}:
        raise ValueError(f"Expected FY{PRIOR_YEAR} and FY{CURRENT_YEAR}; found {sorted(observed)}")
    return sales


def _load_pnl() -> pd.DataFrame:
    raw = pd.read_excel(
        PNL_PATH,
        sheet_name="PnL table",
        header=None,
        usecols="A:M",
        nrows=15,
        engine="openpyxl",
    )
    row_by_label = {
        str(label).strip(): row
        for row, label in raw.iloc[:, 0].items()
        if pd.notna(label)
    }
    required = {
        "gsv": "Gross Sales Value (GSV)",
        "discount": "Discount",
        "turnover": "Turnover (TO)",
        "supply_chain": "Total Supply Chain Cost",
        "gross_profit": "Gross Profit (GP)",
        "marketing": "Marketing Expense",
        "pbo": "Profit before Overheads (PBO)",
    }
    missing = set(required.values()) - set(row_by_label)
    if missing:
        raise ValueError(f"Missing P&L rows: {sorted(missing)}")

    records: list[dict[str, float | int | str]] = []
    for prior_col in range(1, 13, 3):
        brand = raw.iat[0, prior_col]
        if pd.isna(brand):
            continue
        current_col = prior_col + 1
        record: dict[str, float | int | str] = {
            "brand": str(brand).strip(),
            "prior_year": int(raw.iat[1, prior_col]),
            "current_year": int(raw.iat[1, current_col]),
        }
        for metric, label in required.items():
            row = row_by_label[label]
            record[f"{metric}_{PRIOR_YEAR}_keur"] = float(raw.iat[row, prior_col])
            record[f"{metric}_{CURRENT_YEAR}_keur"] = float(raw.iat[row, current_col])
        record["turnover_growth_pct"] = (
            _ratio(record[f"turnover_{CURRENT_YEAR}_keur"], record[f"turnover_{PRIOR_YEAR}_keur"]) - 1
        )
        record["pbo_growth_pct"] = _ratio(record[f"pbo_{CURRENT_YEAR}_keur"], record[f"pbo_{PRIOR_YEAR}_keur"]) - 1
        for year in (PRIOR_YEAR, CURRENT_YEAR):
            record[f"gross_margin_pct_{year}"] = _ratio(
                record[f"gross_profit_{year}_keur"], record[f"turnover_{year}_keur"]
            )
            record[f"pbo_margin_pct_{year}"] = _ratio(
                record[f"pbo_{year}_keur"], record[f"turnover_{year}_keur"]
            )
            record[f"supply_chain_pct_to_{year}"] = _ratio(
                record[f"supply_chain_{year}_keur"], record[f"turnover_{year}_keur"]
            )
        record["gross_margin_movement_bps"] = (
            record[f"gross_margin_pct_{CURRENT_YEAR}"] - record[f"gross_margin_pct_{PRIOR_YEAR}"]
        ) * 10_000
        record["pbo_margin_movement_bps"] = (
            record[f"pbo_margin_pct_{CURRENT_YEAR}"] - record[f"pbo_margin_pct_{PRIOR_YEAR}"]
        ) * 10_000
        record["supply_chain_pct_to_movement_bps"] = (
            record[f"supply_chain_pct_to_{CURRENT_YEAR}"]
            - record[f"supply_chain_pct_to_{PRIOR_YEAR}"]
        ) * 10_000
        records.append(record)
    return pd.DataFrame.from_records(records)


def _load_market() -> pd.DataFrame:
    columns = [
        "channel",
        "segment",
        "manufacturer",
        "brand",
        "sales_value_mat_1_meur",
        "sales_value_mat_meur",
        "source_sales_value_movement_meur",
        "value_share_mat_1_pct",
        "value_share_mat_pct",
        "source_share_movement_pp",
    ]
    market = pd.read_excel(
        MARKET_PATH,
        sheet_name="Market Data",
        header=None,
        skiprows=4,
        usecols="B:K",
        names=columns,
        engine="openpyxl",
    ).dropna(how="all")
    for column in ["channel", "segment", "manufacturer", "brand"]:
        market[column] = market[column].astype("string").str.strip()
    market["market_value_growth_pct"] = (
        _ratio(market["sales_value_mat_meur"], market["sales_value_mat_1_meur"]) - 1
    )
    market["sales_value_movement_meur"] = market["sales_value_mat_meur"] - market["sales_value_mat_1_meur"]
    market["share_movement_pp"] = market["value_share_mat_pct"] - market["value_share_mat_1_pct"]
    return market


MARKET_SEGMENTS = ["Mainstream", "Economy", "Premium"]
SEGMENT_ROW_ORDER = ["Category", *MARKET_SEGMENTS]


def _build_market_segment(market: pd.DataFrame) -> pd.DataFrame:
    """Market size and growth by segment, for the Total and MT channels.

    The workbook gives a Category total per channel plus one row per named brand.
    Segment rows are summed from the named brands, and they do *not* add up to
    Category: the named brands cover roughly 83% of the Total-channel category and
    91% of MT.  ``Category`` is therefore always the file's own number, never a sum
    of the three segments, and ``segment_coverage_pct`` records the gap so a chart
    can state it rather than quietly reconciling it away.
    """
    rows = []
    for channel in ("Total", "MT"):
        block = market.loc[market["channel"].eq(channel)]
        # Named brands only.  The block also carries a Category total and a UniSweet
        # manufacturer total, both with no brand; either one would double-count.
        brands = block.loc[block["manufacturer"].ne("Category") & block["brand"].notna()]
        category = block.loc[block["manufacturer"].eq("Category")].iloc[0]
        unisweet = block.loc[block["manufacturer"].eq("UNISWEET") & block["brand"].isna()].iloc[0]
        coverage = _ratio(brands["sales_value_mat_1_meur"].sum(),
                          category["sales_value_mat_1_meur"]) * 100

        rows.append({
            "channel": channel,
            "segment": "Category",
            "mat1_meur": float(category["sales_value_mat_1_meur"]),
            "mat_meur": float(category["sales_value_mat_meur"]),
            "unisweet_share_movement_pp": float(unisweet["share_movement_pp"]),
            "segment_coverage_pct": float(coverage),
        })
        for segment in MARKET_SEGMENTS:
            part = brands.loc[brands["segment"].eq(segment)]
            ours = part.loc[part["manufacturer"].eq("UNISWEET")]
            rows.append({
                "channel": channel,
                "segment": segment,
                "mat1_meur": float(part["sales_value_mat_1_meur"].sum()),
                "mat_meur": float(part["sales_value_mat_meur"].sum()),
                "unisweet_share_movement_pp": float(ours["share_movement_pp"].sum()),
                "segment_coverage_pct": float(coverage),
            })

    frame = pd.DataFrame(rows)
    frame["growth_pct"] = _ratio(frame["mat_meur"], frame["mat1_meur"]) - 1
    frame["change_meur"] = frame["mat_meur"] - frame["mat1_meur"]
    return frame


def _build_olive_mt_monthly(sales: pd.DataFrame) -> pd.DataFrame:
    """OLIVE gross sales value in the MT channel, by month, prior versus current year.

    The single worst cell in the business: the brand that lost the most value, in
    the channel that lost the most share.
    """
    olive = sales.loc[sales["brand_name"].eq("OLIVE") & sales["channel_code"].eq("MT")]
    wide = (olive.pivot_table(index="month_number", columns="reporting_year",
                              values="gsv_keur", aggfunc="sum")
            .reindex(range(1, 13))
            .fillna(0.0))
    frame = pd.DataFrame({
        "month_number": wide.index.astype(int),
        f"gsv_keur_{PRIOR_YEAR}": wide[PRIOR_YEAR].to_numpy(),
        f"gsv_keur_{CURRENT_YEAR}": wide[CURRENT_YEAR].to_numpy(),
    })
    frame["gsv_change_keur"] = frame[f"gsv_keur_{CURRENT_YEAR}"] - frame[f"gsv_keur_{PRIOR_YEAR}"]
    frame["half"] = np.where(frame["month_number"] <= 6, "H1", "H2")
    return frame


def build_storyline_metrics() -> dict[str, pd.DataFrame]:
    """Build the chart-ready metric registry for the report visual library."""
    sales = _load_sales()
    pnl = _load_pnl()
    market = _load_market()

    total = _annual_sales(sales, []).iloc[0]
    brand = _annual_sales(sales, ["brand_name"])
    channel_internal = _annual_sales(sales, ["channel_code"])
    customer = _annual_sales(sales, ["customer_name", "channel_code"])
    product = _annual_sales(sales, ["product_name"])

    pnl_total = pnl.loc[pnl["brand"].eq("TOTAL")].iloc[0]
    headline = pd.DataFrame(
        [
            ["GSV", total[f"gsv_keur_{PRIOR_YEAR}"], total[f"gsv_keur_{CURRENT_YEAR}"], "kEUR"],
            ["Turnover", total[f"turnover_keur_{PRIOR_YEAR}"], total[f"turnover_keur_{CURRENT_YEAR}"], "kEUR"],
            ["Discount / GSV", total[f"discount_pct_gsv_{PRIOR_YEAR}"], total[f"discount_pct_gsv_{CURRENT_YEAR}"], "%"],
            # Discount stated on Turnover, which is the convention the P&L reports and
            # the one the scorecard quotes. On GSV the same movement barely registers.
            ["Discount / TO",
             _ratio(pnl_total[f"discount_{PRIOR_YEAR}_keur"], pnl_total[f"turnover_{PRIOR_YEAR}_keur"]),
             _ratio(pnl_total[f"discount_{CURRENT_YEAR}_keur"], pnl_total[f"turnover_{CURRENT_YEAR}_keur"]),
             "%"],
            ["Gross Margin", pnl_total[f"gross_margin_pct_{PRIOR_YEAR}"], pnl_total[f"gross_margin_pct_{CURRENT_YEAR}"], "%"],
            ["Gross Profit", pnl_total[f"gross_profit_{PRIOR_YEAR}_keur"], pnl_total[f"gross_profit_{CURRENT_YEAR}_keur"], "kEUR"],
            ["Marketing Expense", pnl_total[f"marketing_{PRIOR_YEAR}_keur"], pnl_total[f"marketing_{CURRENT_YEAR}_keur"], "kEUR"],
            ["PBO", pnl_total[f"pbo_{PRIOR_YEAR}_keur"], pnl_total[f"pbo_{CURRENT_YEAR}_keur"], "kEUR"],
            ["PBO Margin", pnl_total[f"pbo_margin_pct_{PRIOR_YEAR}"], pnl_total[f"pbo_margin_pct_{CURRENT_YEAR}"], "%"],
        ],
        columns=["metric", f"value_{PRIOR_YEAR}", f"value_{CURRENT_YEAR}", "unit"],
    )
    headline["absolute_change"] = headline[f"value_{CURRENT_YEAR}"] - headline[f"value_{PRIOR_YEAR}"]
    headline["growth_pct"] = _ratio(headline[f"value_{CURRENT_YEAR}"], headline[f"value_{PRIOR_YEAR}"]) - 1

    prior_discount_rate = float(total[f"discount_pct_gsv_{PRIOR_YEAR}"])
    gsv_base_effect = float(total["gsv_change_keur"] * (1 - prior_discount_rate))
    discount_intensity_effect = float(
        total[f"gsv_keur_{CURRENT_YEAR}"]
        * (total[f"discount_pct_gsv_{PRIOR_YEAR}"] - total[f"discount_pct_gsv_{CURRENT_YEAR}"])
    )
    topline_bridge = pd.DataFrame(
        {
            "step": [f"FY{PRIOR_YEAR} TO", "Lower GSV base", "Higher discount intensity", f"FY{CURRENT_YEAR} TO"],
            "kind": ["total", "change", "change", "total"],
            "value_keur": [
                total[f"turnover_keur_{PRIOR_YEAR}"],
                gsv_base_effect,
                discount_intensity_effect,
                total[f"turnover_keur_{CURRENT_YEAR}"],
            ],
        }
    )

    market_total = market.loc[
        market["channel"].eq("Total")
        & market["manufacturer"].eq("UNISWEET")
        & market["brand"].isna()
    ].iloc[0]
    market_brands = market.loc[
        market["channel"].eq("Total")
        & market["manufacturer"].eq("UNISWEET")
        & market["brand"].notna()
    ].copy()
    bridge_order = ["OLIVE", "SKY", "COBALT"]
    market_brands["brand"] = pd.Categorical(market_brands["brand"], bridge_order, ordered=True)
    market_brands = market_brands.sort_values("brand")
    brand_share_movements = market_brands["share_movement_pp"].tolist()
    source_rounding = float(
        market_total["value_share_mat_pct"]
        - market_total["value_share_mat_1_pct"]
        - sum(brand_share_movements)
    )
    market_share_bridge = pd.DataFrame(
        {
            "step": [
                "MAT-1 UniSweet share",
                *bridge_order,
                "Source rounding",
                "MAT UniSweet share",
            ],
            "kind": ["total", "change", "change", "change", "change", "total"],
            "value_pp": [
                market_total["value_share_mat_1_pct"],
                *brand_share_movements,
                source_rounding,
                market_total["value_share_mat_pct"],
            ],
        }
    )

    market_channel = market.loc[
        market["channel"].isin(["DT", "MT"])
        & market["manufacturer"].eq("UNISWEET")
        & market["brand"].isna()
    ][["channel", "market_value_growth_pct", "share_movement_pp"]].copy()
    category_channel = market.loc[
        market["channel"].isin(["DT", "MT"])
        & market["manufacturer"].eq("Category")
    ][["channel", "market_value_growth_pct"]].rename(
        columns={"market_value_growth_pct": "category_growth_pct"}
    )
    competitor = market.loc[
        market["channel"].isin(["DT", "MT"])
        & market["manufacturer"].str.startswith("COMPETITOR", na=False)
    ].copy()
    competitor = competitor.loc[competitor.groupby("channel")["share_movement_pp"].idxmax()][
        ["channel", "brand", "share_movement_pp"]
    ].rename(columns={"brand": "competitor", "share_movement_pp": "competitor_share_movement_pp"})
    channel = (
        channel_internal.rename(columns={"channel_code": "channel"})
        .merge(market_channel, on="channel", how="inner", validate="one_to_one")
        .merge(category_channel, on="channel", how="left", validate="one_to_one")
        .merge(competitor, on="channel", how="left", validate="one_to_one")
        .sort_values("channel")
    )

    monthly = (
        sales.groupby(["month_number", "reporting_year"], as_index=False)[
            ["gsv_keur", "turnover_keur", "discount_keur"]
        ]
        .sum()
        .pivot(index="month_number", columns="reporting_year")
    )
    monthly.columns = [f"{metric}_{int(year)}" for metric, year in monthly.columns]
    monthly = monthly.reset_index()
    monthly["to_change_keur"] = monthly[f"turnover_keur_{CURRENT_YEAR}"] - monthly[f"turnover_keur_{PRIOR_YEAR}"]
    monthly["to_growth_pct"] = _ratio(monthly[f"turnover_keur_{CURRENT_YEAR}"], monthly[f"turnover_keur_{PRIOR_YEAR}"]) - 1
    monthly["half"] = np.where(monthly["month_number"].le(6), "H1", "H2")

    priority_customers = ["Bliss", "Candies", "Macarons"]
    priority_products = ["POUCH 900GR", "PACK 1.1KG", "POUCH 100GR", "POUCH 400GR"]
    customer_sku = _annual_sales(
        sales.loc[
            sales["brand_name"].eq("OLIVE")
            & sales["customer_name"].isin(priority_customers)
            & sales["product_name"].isin(priority_products)
        ],
        ["customer_name", "channel_code", "brand_name", "product_name"],
    )
    customer_sku["customer_name"] = pd.Categorical(
        customer_sku["customer_name"], priority_customers, ordered=True
    )
    customer_sku["product_name"] = pd.Categorical(
        customer_sku["product_name"], priority_products, ordered=True
    )
    customer_sku = customer_sku.sort_values(["customer_name", "product_name"])

    pbo_bridge = pd.DataFrame(
        {
            "step": [f"FY{PRIOR_YEAR} PBO", "Gross Profit change", "Marketing savings", f"FY{CURRENT_YEAR} PBO"],
            "kind": ["total", "change", "change", "total"],
            "value_keur": [
                pnl_total[f"pbo_{PRIOR_YEAR}_keur"],
                pnl_total[f"gross_profit_{CURRENT_YEAR}_keur"] - pnl_total[f"gross_profit_{PRIOR_YEAR}_keur"],
                -(pnl_total[f"marketing_{CURRENT_YEAR}_keur"] - pnl_total[f"marketing_{PRIOR_YEAR}_keur"]),
                pnl_total[f"pbo_{CURRENT_YEAR}_keur"],
            ],
        }
    )

    portfolio = (
        brand[["brand_name", "to_growth_pct"]]
        .rename(columns={"brand_name": "brand", "to_growth_pct": "internal_to_growth_pct"})
        .merge(
            market_brands[["brand", "market_value_growth_pct", "share_movement_pp"]].assign(
                brand=lambda frame: frame["brand"].astype("string")
            ),
            on="brand",
            how="inner",
            validate="one_to_one",
        )
        .merge(
            pnl.loc[pnl["brand"].ne("TOTAL"), ["brand", "pbo_growth_pct", "gross_margin_movement_bps"]],
            on="brand",
            how="left",
            validate="one_to_one",
        )
    )

    action_cards = pd.DataFrame(
        [
            ["1", "OLIVE customer x SKU recovery", "Sales Head", "Weeks 0-2: approve baseline and economics", "Incremental GP and PBO"],
            ["2", "Trade-spend and discount ROI reset", "Sales Head", "Classify spend: keep, test, redesign or stop", "Promotion ROI and Discount/GSV"],
            ["3", "Selective reinvestment with guardrails", "Finance Head", "Release scale funding only after positive incremental GP", "Incremental PBO and payback"],
        ],
        columns=["action", "title", "owner", "first_gate", "core_kpi"],
    )

    raw_by_year = sales.groupby("reporting_year", as_index=False)[
        ["gsv_keur", "turnover_keur", "discount_keur"]
    ].sum()
    pnl_reconciliation = raw_by_year.copy()
    for metric, pnl_metric in [
        ("gsv_keur", "gsv"),
        ("turnover_keur", "turnover"),
        ("discount_keur", "discount"),
    ]:
        pnl_reconciliation[f"pnl_{metric}"] = pnl_reconciliation["reporting_year"].map(
            {
                PRIOR_YEAR: pnl_total[f"{pnl_metric}_{PRIOR_YEAR}_keur"],
                CURRENT_YEAR: pnl_total[f"{pnl_metric}_{CURRENT_YEAR}_keur"],
            }
        )
        pnl_reconciliation[f"check_{metric}"] = (
            pnl_reconciliation[metric] - pnl_reconciliation[f"pnl_{metric}"]
        )

    flagged = sales.loc[
        sales["data_quality_flags"].fillna("").str.contains("TURNOVER_GT_GSV", regex=False)
    ]
    quality = pd.DataFrame(
        {
            "metric": ["Raw Sales rows", f"Flagged TO > GSV TO FY{PRIOR_YEAR}", f"Flagged TO > GSV TO FY{CURRENT_YEAR}"],
            "value": [
                len(sales),
                flagged.loc[flagged["reporting_year"].eq(PRIOR_YEAR), "turnover_keur"].sum(),
                flagged.loc[flagged["reporting_year"].eq(CURRENT_YEAR), "turnover_keur"].sum(),
            ],
        }
    )

    registry = {
        "headline": headline,
        "topline_bridge": topline_bridge,
        "market_share_bridge": market_share_bridge,
        "market_segment": _build_market_segment(market),
        "olive_mt_monthly": _build_olive_mt_monthly(sales),
        "channel": channel,
        "monthly": monthly,
        "customer": customer,
        "product": product,
        "customer_sku": customer_sku,
        "pbo_bridge": pbo_bridge,
        "pnl": pnl,
        "portfolio": portfolio,
        "action_cards": action_cards,
        "pnl_reconciliation": pnl_reconciliation,
        "quality": quality,
    }
    return registry


STORYLINE_DATAFRAMES = build_storyline_metrics()


if __name__ == "__main__":
    for name, frame in STORYLINE_DATAFRAMES.items():
        print(f"{name}: {len(frame):,} rows x {len(frame.columns)} columns")

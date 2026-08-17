"""Build one chart of every supported type from real UniSweet data.

This is the smoke test for swd.py: run it, look at gallery/*.png, then lint it.
Every chart here is a worked example of the pattern named in its filename.

    python demo.py                 # writes gallery/
    python lint.py demo.py         # should report 0 errors
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

import swd

HERE = Path(__file__).resolve().parent
OUT = HERE / "gallery"


def _find_project_root() -> Path:
    """Walk up for the exported chart data this gallery is built from.

    Searched rather than hard-coded by depth, because this file is also installed
    outside the repository as a skill. There it has no data to draw on, and the
    error below says so instead of raising a bare FileNotFoundError.
    """
    for candidate in (HERE, *HERE.parents):
        if (candidate / "outputs" / "report_visuals" / "data").is_dir():
            return candidate
    raise FileNotFoundError(
        "demo.py builds its gallery from this project's exported chart data and "
        "cannot find outputs/report_visuals/data/ above "
        f"{HERE}. Run it from inside the UniSweet repository, after "
        "visualisations.ipynb has exported the charts."
    )


def rows(name: str) -> list[dict]:
    root = _find_project_root()
    path = root / "outputs" / "report_visuals" / "data" / name
    if not path.exists():
        # Retired visuals keep their exported data under archive/data/. The gallery
        # is a catalogue of chart *forms*, so it goes on using whichever real series
        # suits each form best, whether or not it is still in the current deck.
        path = root / "outputs" / "report_visuals" / "archive" / "data" / name
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def m(v) -> float:
    """kEUR -> EURm."""
    return float(v) / 1000.0


def save(fig, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", facecolor="white")
    print(f"wrote gallery/{name}.png")


# --- 1. simple text: one number does not need a chart ------------------------
def chart_bignum():
    fig, ax = swd.figure(
        "Profit margin rose 393 bps while the topline shrank",
        subtitle="PBO margin, FY2024 vs FY2023",
        source="Source: P&L Table.xlsx | Margin gain is spend-driven, not trading-driven",
        figsize=(12.8, 6.0))
    swd.bignum(ax, "+393 bps",
               "PBO margin, on turnover down 6.7% - lower marketing spend, not better trading")
    save(fig, "01_simple_text")


# --- 2. horizontal bar: the go-to for categorical data -----------------------
def chart_hbar():
    data = rows("06_customer_concentration.csv")
    labels = [r["customer_name"] for r in data]
    values = [m(r["to_change_keur"]) for r in data]

    fig, ax = swd.figure(
        "Three customers explain 91% of the turnover decline",
        subtitle="Change in turnover by customer, FY2024 vs FY2023, EURm",
        source="Source: outputs/sales_master.csv | Existing-customer spend, not customer attrition")
    swd.hbar(ax, labels, values, highlight={"Bliss", "Macarons", "Candies"},
             unit="", decimals=1, sort=True)
    # Annotation goes in whitespace, in data coordinates - here the empty band
    # to the left of the short "all other" bar.
    swd.annotate(ax, "Everyone else nets to -1.8m:\nthis is a three-account problem",
                 xy=(-6.4, 3.0), bold=True)
    save(fig, "02_horizontal_bar")


# --- 3. vertical bar: change over a consistent interval ----------------------
def chart_bar():
    data = rows("05_monthly_to_change.csv")
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    labels = [names[int(r["month_number"]) - 1] for r in data]
    values = [m(r["to_change_keur"]) for r in data]
    h2 = {lab for lab, r in zip(labels, data) if r["half"] == "H2"}

    fig, ax = swd.figure(
        "96% of the turnover decline landed in the second half",
        subtitle="Monthly change in turnover, FY2024 vs FY2023, EURm",
        source="Source: outputs/sales_master.csv | Sell-in timing; does not establish seasonal causality")
    swd.bar(ax, labels, values, highlight=h2, decimals=1)
    save(fig, "03_vertical_bar")


# --- 4. line: continuous data, labelled at the end ---------------------------
def chart_line():
    data = rows("05_monthly_to_change.csv")
    months = list(range(1, 13))
    series = {
        "FY2023": [m(r["gsv_keur_2023"]) for r in data],
        "FY2024": [m(r["gsv_keur_2024"]) for r in data],
    }
    fig, ax = swd.figure(
        "FY2024 ran below the prior year every month from August",
        subtitle="Gross sales value by month, EURm",
        source="Source: outputs/sales_master.csv")
    swd.line(ax, months, series, highlight={"FY2024"})
    ax.set_xticks(months)
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax.set_ylabel("GSV (EURm)")
    save(fig, "04_line")


# --- 5. slopegraph: two points in time, several categories -------------------
def chart_slopegraph():
    data = {r["channel"]: r for r in rows("04b_channel_share_hotspot.csv")}
    series = {
        "Total": (21.9, 22.5),
        "DT": (float(data["DT"]["discount_pct_gsv_2023"]) * 100,
               float(data["DT"]["discount_pct_gsv_2024"]) * 100),
        "MT": (float(data["MT"]["discount_pct_gsv_2023"]) * 100,
               float(data["MT"]["discount_pct_gsv_2024"]) * 100),
    }
    fig, ax = swd.figure(
        "Discount intensity rose in both channels, not just one",
        subtitle="Discount as % of GSV",
        source="Source: outputs/sales_master.csv | Diagnostic only; does not establish promotion causality")
    swd.slopegraph(ax, "FY2023", "FY2024", series, highlight={"MT"}, unit="%", decimals=1)
    save(fig, "05_slopegraph")


# --- 6. waterfall: start, increments, end ------------------------------------
def chart_waterfall():
    fig, ax = swd.figure(
        "Lower marketing spend more than offset the gross profit decline",
        subtitle="Profit before overheads bridge, EURm",
        source="Source: P&L Table.xlsx | Supply Chain Cost / TO worsened ~35 bps: not efficiency")
    swd.waterfall(ax,
                  labels=["Gross profit", "Marketing spend"],
                  deltas=[-10.3, 15.5],
                  start=80.7,
                  start_label="FY2023 PBO",
                  end_label="FY2024 PBO",
                  decimals=1)
    save(fig, "06_waterfall")


# --- 7. heatmap: keep the table, add a visual cue ----------------------------
def chart_heatmap():
    # Colour saturation and the printed number must encode the SAME thing in
    # the same direction, or the reader is being told two different stories.
    data = rows("05_monthly_to_change.csv")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    matrix = [
        [float(r["discount_keur_2023"]) / float(r["gsv_keur_2023"]) * 100 for r in data],
        [float(r["discount_keur_2024"]) / float(r["gsv_keur_2024"]) * 100 for r in data],
    ]
    fig, ax = swd.figure(
        "Discount intensity ran hotter in almost every month of FY2024",
        subtitle="Discount as % of GSV, by month",
        source="Source: outputs/sales_master.csv | Diagnostic only; does not establish promotion causality",
        figsize=(13.6, 5.0))
    swd.heatmap(ax,
                row_labels=["FY2023", "FY2024"],
                col_labels=months,
                matrix=matrix,
                fmt="{:.1f}",
                legend_label="lighter = lower discount %   ->   darker = higher discount %")
    save(fig, "07_heatmap")


def main() -> None:
    swd.use()
    chart_bignum()
    chart_hbar()
    chart_bar()
    chart_line()
    chart_slopegraph()
    chart_waterfall()
    chart_heatmap()
    print(f"\n{len(plt.get_fignums())} figures built in {OUT}")


main()

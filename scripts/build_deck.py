"""Build the UniSweet FY2024 review deck.

One spec, two renderings - a sparse .pptx for the room and an annotated .pdf for
everyone who was not in it. See toolkit/slides/SKILL.md for why.

Action titles are read from outputs/report_visuals/visual_manifest.csv rather
than retyped, so the deck and the charts cannot drift apart.

    python3 scripts/build_deck.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RENDERER_DIR = PROJECT_ROOT / "toolkit" / "slides"
if str(RENDERER_DIR) not in sys.path:
    sys.path.insert(0, str(RENDERER_DIR))

from deck import Slide, build_pdf, build_pptx  # noqa: E402

VISUALS = PROJECT_ROOT / "outputs" / "report_visuals"
SLIDE_PNG = VISUALS / "slides"
OUT = PROJECT_ROOT / "outputs" / "deck"

MANIFEST = pd.read_csv(VISUALS / "visual_manifest.csv").set_index("visual_id")

SALES = "outputs/sales_master.csv"
PNL = "P&L Table.xlsx"
MARKET = "Market Report MAT Nov'24.xlsx"


def chart(visual_id: str, *, eyebrow: str, subtitle: str, takeaway: str, narration: str) -> Slide:
    """A chart slide. The action title, source and caveat all come from the manifest.

    The caveat rides the source line rather than staying on the full-size chart
    export. The slide twin hides the figure's own footer, so a caveat left there
    would reach nobody reading the deck - which is everybody this pack is for.
    """
    row = MANIFEST.loc[visual_id]
    source = row["source"]
    if isinstance(row["caveat"], str) and row["caveat"].strip():
        source = f"{source}  |  {row['caveat']}"
    return Slide(
        kind="chart",
        title=row["action_title"],
        subtitle=subtitle,
        takeaway=takeaway,
        narration=narration,
        image=SLIDE_PNG / f"{visual_id}.png",
        source=source,
        eyebrow=eyebrow,
    )


# Six exhibits, one line of argument. Read the titles alone and they should be the
# story: the KPIs fell, the market did not, MT is where it broke, OLIVE broke in H2,
# profit survived only on cost, and the growth left is COBALT and SKY.
SLIDES: list[Slide] = [
    Slide(
        kind="title",
        title="FY2024 performance review",
        subtitle="UniSweet Leadership and Finance Business Partners\n"
                 "Prepared from Sales, P&L and Market data  |  FY2024 versus FY2023",
        narration="This pack is built to be read without me. Every slide states its "
                  "conclusion in the title, and the reasoning sits underneath it.",
        source=f"{SALES}, {PNL} and {MARKET}",
    ),

    Slide(
        kind="summary",
        eyebrow="The route",
        title="The argument runs in six steps, and the answer comes first",
        bullets=[
            "1.  How bad is it?  —  the three topline KPIs",
            "2.  Did the market do this to us?  —  category and segment growth",
            "3.  Where exactly did it break?  —  the channel, then one brand inside it",
            "4.  Why did PBO still rise?  —  marketing and supply chain cost by brand",
            "5.  What is left to grow?  —  COBALT and SKY against their own markets",
            "6.  What we are asking for  —  three gated actions, owners named",
        ],
        takeaway="Six questions, six exhibits. Read the titles alone and you have the argument.",
        narration="Questions 1 and 2 establish how serious this is and whose problem it is. "
                  "Questions 3 and 4 locate the damage and explain the profit result. "
                  "Questions 5 and 6 are what we do about it.",
        source=f"{SALES}, {PNL} and {MARKET}",
    ),

    Slide(
        kind="statement",
        eyebrow="The answer, up front",
        title="Profit rose, but the business did not get healthier",
        bullets=[
            "Topline and share fell. Lower spend alone protected PBO.",
            "Restore profitable growth without giving back the protected profit.",
        ],
        takeaway="Every favourable line in this year's P&L is a cost line.",
        narration="I am leading with the conclusion rather than walking you through the analysis. "
                  "The €15.5m taken out of marketing is larger than the €10.3m of Gross Profit "
                  "lost — that gap, and nothing about demand, is why PBO is up.",
        source=f"{SALES}, {PNL} and {MARKET}",
    ),

    chart("01_scorecard_to_gsv_discount",
          eyebrow="Where we ended up  |  1 of 6",
          subtitle="FY2024 versus FY2023",
          takeaway="Three KPIs, three adverse moves — and the discount rate made the last one worse.",
          narration="Turnover fell €19.6m and GSV €22.3m. Turnover fell the faster of the two "
                    "because discount on Turnover rose 103bps at the same time."),

    chart("02_market_growth_total",
          eyebrow="Did the market do this to us?  |  2 of 6",
          subtitle="Market sales value, EURm  |  MAT Nov'24 versus MAT-1",
          takeaway="No. The category fell 1.3% and we fell 4.3% — the gap is ours to explain.",
          narration="Economy grew 17.7% and Premium 3.9%. The decline is Mainstream, which is "
                    "where 79% of our turnover sits, and where we gave back 2.98 share points."),

    chart("03_market_growth_mt",
          eyebrow="Where did it break?  |  3 of 6",
          subtitle="Market sales value, EURm  |  Modern Trade only",
          takeaway="Modern Trade. Same category decline, six times the share loss.",
          narration="MT Mainstream fell 13.8% while MT Economy grew 41.4%, most of it LILAC at "
                    "+5.53 points. DT lost only 0.28 share points against MT's 6.07."),

    chart("04_olive_mt_monthly_gsv",
          eyebrow="Where did it break?  |  4 of 6",
          subtitle="OLIVE gross sales value in Modern Trade, EURm per month",
          takeaway="A second-half problem in one brand and one channel — which narrows the fix.",
          narration="H1 was down €2.99m, H2 down €5.74m. November is the only month above "
                    "FY2023. Monthly sell-in does not by itself establish seasonality."),

    chart("05_cost_by_brand",
          eyebrow="Why did PBO still rise?  |  5 of 6",
          subtitle="Marketing expense and total supply chain cost, EURm",
          takeaway="PBO protection is cost-led. It is repeatable once, maybe twice.",
          narration="OLIVE marketing fell 30% and supply chain 5%. Supply chain cost per euro "
                    "of Turnover still worsened 35bps, so this is a smaller base, not efficiency."),

    chart("06_revenue_cobalt_sky",
          eyebrow="What is left to grow?  |  6 of 6",
          subtitle="Turnover, EURm  |  Against each brand's own market",
          takeaway="One brand to scale on evidence, one to diagnose before funding.",
          narration="COBALT grew 11.6% against a market up 3.9% and gained 0.56 share points. "
                    "SKY fell 7.4% while its market grew 23.8% — reconcile that before spending."),

    Slide(
        kind="closing",
        eyebrow="The ask",
        title="Approve the three week-0 gates today",
        bullets=[
            ("ACTION 1  ·  SALES HEAD", "Approve the OLIVE × Modern Trade recovery baseline "
                                        "and its customer × SKU economics, weeks 0-2."),
            ("ACTION 2  ·  SALES HEAD", "Approve classifying trade spend into keep, test, "
                                        "redesign or stop before any budget is restored."),
            ("ACTION 3  ·  FINANCE HEAD", "Agree scale funding is released only after positive "
                                          "incremental Gross Profit — COBALT first, SKY only after diagnosis."),
            ("IF WE DO NOTHING", "The marketing lever cannot be pulled twice; FY2025 PBO carries "
                                 "the full topline decline."),
        ],
        takeaway="Restore profitable growth without giving back the protected PBO.",
        narration="Each action has a first gate rather than a budget, so the decision today is "
                  "to start, not to spend. Owners are named and the KPIs are already defined.",
        source="references/domain/calls-to-action-by-audience.md",
    ),

    Slide(
        kind="summary",
        eyebrow="Appendix  |  How to read this pack",
        title="Sources, definitions and what this analysis does not claim",
        bullets=[
            ("INTERNAL SALES", f"{SALES} — every row retained, so GSV, Discount and TO tie "
                               "exactly to the P&L"),
            ("P&L", f"inputs/pnl/{PNL}. Marketing and supply chain cost are stated assumptions, "
                    "not measured spend"),
            ("MARKET", f"inputs/market/{MARKET} — MAT sell-out, a different clock from internal "
                       "FY sell-in"),
            ("TWO LIMITS WORTH STATING", "Segment rows sum named brands only (82.9% at Total, "
                                         "90.9% in MT); category growth is identical in every channel"),
            ("NOT CLAIMED", "Discount movement is not causality. Lower cost is not efficiency. "
                            "SKY's divergence is a question."),
        ],
        narration="These are the qualifications I would give verbally, written down because this "
                  "pack will be read without me. Every chart has a matching CSV in "
                  "outputs/report_visuals/data/.",
        source="STORYLINE_METRIC_FRAMEWORK.md and visualisations.ipynb",
    ),
]


def main() -> None:
    pptx_path = build_pptx(SLIDES, OUT / "UniSweet-FY2024-Review.pptx")
    pdf_path = build_pdf(SLIDES, OUT / "UniSweet-FY2024-Review-circulated.pdf")
    print(f"{len(SLIDES)} slides")
    print(f"  live       {pptx_path.relative_to(PROJECT_ROOT)}")
    print(f"  circulated {pdf_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()

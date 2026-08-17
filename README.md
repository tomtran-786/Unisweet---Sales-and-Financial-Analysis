# UniSweet FY2024 Performance Review

A Finance Business Partner case study, taken from raw customer workbooks to a leadership
deck. This repository holds the whole path: the data cleaning, the metric layer, the charts,
and the presentation that argues from them.

**→ [Read the deck (PDF)](outputs/deck/UniSweet-FY2024-Review-circulated.pdf)**  ·
[Live version (PPTX)](outputs/deck/UniSweet-FY2024-Review.pptx)  ·
[Individual charts](outputs/report_visuals/)

---

## 1 · The problem

**SEO-V x Unilever Vietnam — "Performance Strategy Reset to Reignite the Confectionery
Growth"**, the case study for the **Finance Business Partner Intern** position.

UniSweet is a global confectionery business. It is still the category leader, but it has
entered what the brief calls a period of *structural performance deceleration*. The role in
the case is Performance Management inside the Finance Business Partner team: turning
performance data into something a board can act on.

The task is to lead the preliminary analysis for the **Monthly Leadership Meeting**, where
the board reviews business and financial performance and agrees what to do about it. The
brief sets four questions:

| | Question | Source it must be answered from |
|---|---|---|
| 1 | **Market** — what are the dynamics, trends and segmentation shifts shaping the category's growth outlook? | Nielsen market report |
| 2 | **Sales** — what are the underlying trends in sales and in Discount % Turnover (`Discount = GSV − TO`) across brands, products, channels and customers? | Internal sales extracts |
| 3 | **Financial** — how did 2023 and 2024 compare, year on year? | P&L table |
| 4 | **Strategy** — which **three** actions close the performance gaps? | All of the above |

The management question underneath all four: *the profit line improved while the business
weakened — is that a result to defend or a warning to act on?*

---

## 2 · The solution

### What the data is

Four sources, three different grains, two different clocks.

| Source | Files | Grain | Period |
|---|---|---|---|
| **Internal sales** | `inputs/sales/Cust 1–27.xlsx` — 27 workbooks, 8 columns each (`Customer Code`, `Brand Code`, `Pack Type`, `Pack Size`, `Month`, `Year`, `KPI`, `Values`) | long format, one row per KPI reading | 2022–2024 |
| **Mapping** | `inputs/mapping/Master Mapping.xlsx` — 3 sheets: Customer (29 rows, carries Channel), Brand (10), Product (16) | lookup tables | — |
| **P&L** | `inputs/pnl/P&L Table.xlsx`, sheet `PnL table` | Brand × Year, in kEUR and mVND | 2023, 2024 |
| **Market** | `inputs/market/Market Report MAT Nov'24.xlsx`, sheet `Market Data` | Channel × Segment × Manufacturer × Brand | MAT Nov'24 vs MAT-1 |

The sales extracts arrive as 27 separate files in long format, where GSV and Turnover for the
same product-month sit on two different rows. Nothing joins them to a customer name, a
channel or a product group until the mapping is applied.

### How it was cleaned

[`scripts/build_sales_master.py`](scripts/build_sales_master.py) is the only data-processing
step, and it is deliberately one readable file:

1. Auto-discovers every `Cust *.xlsx` and validates the eight expected source columns.
2. Normalises `Customer Code`, `Brand Code`, `Month`, `Pack Type` and `Pack Size` —
   customer codes keep their leading zeros, which is why they must be read back as strings.
3. Pivots the long `KPI`/`Values` pair into `gsv_keur` and `turnover_keur` on a single grain:
   `Reporting Month × Customer × Brand × Pack Type × Pack Size`.
4. Joins customer/channel, brand and product mappings.
5. Derives `discount_keur = gsv_keur − turnover_keur` and both discount rates.
6. Applies quality flags and records the source file and source row behind every value, so
   any number can be traced back to the cell it came from.

The result is **10,175 rows** (3,222 in 2022, 3,305 in 2023, 3,648 in 2024). What the flags
found:

| Status | Rows | |
|---|---:|---|
| `VALID` | 8,559 | no flags |
| `REVIEW` | 1,229 | flagged but usable |
| `INVALID` | 387 | blocked from the certified base |

| Flag | Rows | What it means |
|---|---:|---|
| `PRODUCT_MAPPING_REVIEW` | 1,213 | product hierarchy needs confirmation |
| `TURNOVER_GT_GSV` | 312 | Turnover exceeds GSV, which implies a negative discount |
| `TURNOVER_NEGATIVE` | 136 | negative Turnover — returns, or a sign convention |
| `GSV_DUPLICATE` / `TURNOVER_DUPLICATE` | 75 / 75 | more than one source row on the same grain |

**Two bases, kept deliberately apart.** This is the decision worth understanding before
reading any number in the deck:

- The **reporting base** keeps every row. That is why Sales reconciles *exactly* to the P&L
  at both total and brand level — GSV 371,528.3 → 349,247.6 kEUR, matching the P&L to the
  decimal. It also means the 312 unvalidated `TURNOVER_GT_GSV` rows are included.
- The **certified base** (`certified_for_analysis`, 9,788 rows) screens those rows out. It is
  used only as a data-quality sensitivity, never as the headline source.

The deck quotes the reporting base because that is the base management reports on. The
notebook's appendix re-runs the storyline's claims against the certified base to show which
of them would move. Full definitions in
[STORYLINE_METRIC_FRAMEWORK.md](STORYLINE_METRIC_FRAMEWORK.md).

### How the data becomes an argument

```text
inputs/sales/*.xlsx + Master Mapping.xlsx
        ↓  scripts/build_sales_master.py
outputs/sales_master.csv
        ↓  scripts/storyline_metrics.py          (+ P&L, + Market)
chart-ready metric frames
        ↓  visualisations.ipynb
6 charts  →  PNG + SVG + CSV + headerless slide twins
        ↓  scripts/build_deck.py
UniSweet-FY2024-Review.pptx   (live)
UniSweet-FY2024-Review-circulated.pdf   (circulated)
```

Two properties of this pipeline are worth stating, because they are what keep it honest:

- **Titles are never retyped.** [`scripts/build_deck.py`](scripts/build_deck.py) reads each
  slide's action title and source line out of `outputs/report_visuals/visual_manifest.csv`,
  which the notebook writes. A chart and the slide that carries it cannot drift apart.
- **Every chart exports its own data.** Each figure writes the exact frame behind it to
  `outputs/report_visuals/data/`, so any figure on any slide can be traced without asking
  the analyst for the working.

The deck is **one specification, two renderings**: a sparse PPTX for the room, where the
takeaway and narration live in the speaker notes, and a PDF for everyone who was not in the
room, where the same text is printed on the page.

### What it concludes

> **Profit rose, but the business did not get healthier.** The category fell 1.3% while
> UniSweet fell 4.3%. Modern Trade gave back 6.07 share points. PBO still rose 6.4% — but
> only because marketing spend fell €15.5m against €10.3m of lost Gross Profit. That is a
> lever that cannot be pulled twice.

The three actions the deck asks the board to approve:

| | Action | Owner |
|---|---|---|
| 1 | Approve the OLIVE × Modern Trade recovery baseline and its customer × SKU economics, weeks 0–2 | Sales Head |
| 2 | Classify trade spend into keep, test, redesign or stop before any budget is restored | Sales Head |
| 3 | Release scale funding only after positive incremental Gross Profit — COBALT first, SKY only after diagnosis | Finance Head |

### Reproduce it

```bash
python -m pip install -r requirements.txt
```

```bash
python scripts/build_sales_master.py
```

```bash
python -m jupyter nbconvert --to notebook --execute --inplace visualisations.ipynb
```

```bash
python scripts/build_deck.py
```

```bash
pytest -p no:cacheprovider
```

Every step above runs from a fresh clone. The chart and slide libraries the notebook and the
deck builder import live in [`toolkit/`](toolkit/), with nothing outside `requirements.txt`.

Reading the master back:

```python
import pandas as pd

sales = pd.read_csv(
    "outputs/sales_master.csv",
    dtype={"customer_code": "string", "brand_code": "string"},
    parse_dates=["reporting_month"],
)
```

`customer_code` must be read as a string to preserve leading zeros. Add
`sales = sales[sales["certified_for_analysis"]]` to switch to the certified base.

---

## 3 · Limits, and where this goes next

Stated plainly, because the analysis is only as good as what it admits.

**Data quality.** The 312 `TURNOVER_GT_GSV` rows remain unvalidated and are still inside the
reporting base. They carry 2,574.5 kEUR of FY2023 Turnover and 3,173.0 kEUR of FY2024
Turnover. Until the business confirms them, every headline carries that much uncertainty.

**Two different clocks.** Market figures are MAT Nov'24 sell-out; internal figures are
calendar-FY sell-in. They are never the same period, and the deck says so on every slide
that puts them side by side. The COBALT and SKY comparison in particular is a *question*
raised by the divergence, not a measured conclusion.

**Market coverage.** Segment rows sum the named brands only — 82.9% of Category at total
level, 90.9% in Modern Trade. The Category row is the source file's own total, not the sum
of the segments beneath it.

**Cost figures are assumptions.** Marketing and supply chain cost are stated as assumptions
inside the P&L workbook, not measured spend. Every conclusion about cost inherits that.

**Discount is a diagnostic, not a cause.** Discount rates move in both directions across the
losses. Without promotion-level data, no causal claim about pricing is available.

**A source disagreement.** The brief quotes an exchange rate of 26,723 EUR/VND; the P&L
workbook uses 26,743. Nothing in the deck depends on it — every figure is reported in EUR —
but the two sources do not agree.

### Next

- Validate the flagged rows, then re-run the whole storyline on the certified base and
  publish the delta.
- Measure promotion ROI so the discount analysis can move from diagnostic to causal.
- Build the Excel dashboard route, which the brief offers as an alternative deliverable with
  its own layout spec in `references/source-briefs/`.

---

## 4 · The method: applying *Storytelling with Data*

Every visual decision in this repository comes from Cole Nussbaumer Knaflic's
**Storytelling with Data: A Data Visualization Guide for Business Professionals**
(Wiley, 2015). The point of this section is that the principles are not applied by taste —
they are written down as code that runs, in [`toolkit/charts/`](toolkit/charts/): `swd.py`
builds the chart forms the book recommends, and `lint.py` fails a figure that breaks its
rules. Every chart in the deck is linted at export and the result is recorded in
`visual_manifest.csv`. All six read `clean`.

The path from book to library is described in [`toolkit/README.md`](toolkit/README.md):
the books were converted from PDF to Markdown, the parts that are *decisions* were distilled
into short notes in original words with attribution, and the parts that are *mechanical*
became functions and lint checks. The converted book text and extracted figures themselves
stay local and are gitignored — only the distillations and the code are published here.

### Choosing the story before choosing the chart

The book's first move is to settle the context before drawing anything: who the audience is,
what you need them to do, and only then how the data supports it. Three answers were fixed
before the first figure existed:

- **Who** — the board at the Monthly Leadership Meeting. One decision maker, not
  "stakeholders".
- **What** — approve three week-0 gates. A verb, not a briefing.
- **How** — six exhibits, one line of argument.

That produced a Big Idea in a single sentence — *profit rose but the business did not get
healthier* — and a narrative arc the slide order follows literally: **how bad is it → did the
market do this to us → where exactly did it break → why did PBO still rise → what is left to
grow → what we are asking for.** Read the six titles alone and they are the story.

Every title is an **action title**: a claim the chart has to defend, never a topic label. Not
"Market Analysis" but *"The category barely moved; Mainstream is where the value went"*. This
is enforced, not encouraged — `swd.figure()` refuses to build a figure without one, and
`lint.py` warns when a title reads as a subject heading.

### Choosing metrics that carry the claim

The book's discipline about context applies to measures too: the metric has to be the one the
argument needs, and any other reasonable reading has to be disclosed rather than quietly
dropped. Four choices in this project:

- **Discount on Turnover, not on GSV.** The P&L reports it on Turnover, so the scorecard does
  too: 28.08% → 29.11%, +103bps. Read on GSV the same movement is +62bps. Both numbers are in
  the metric layer and the smaller reading is printed in the chart's own caveat line, so
  nobody has to discover it later.
- **Market growth by segment, not by brand.** The claim is about *where* value went, so the
  rows are Category, Mainstream, Economy and Premium — the shape of the question, not the
  shape of the source table.
- **Sell-in and sell-out never merged.** Internal figures are FY sell-in; market figures are
  MAT sell-out. They appear side by side only where the divergence is the point, and the
  slide says so.
- **Favourable is not the same as positive.** A €15.5m *cut* in marketing spend is good for
  the business, so it is drawn in the favourable colour even though it prints with a minus
  sign. Direction is decided by what a number means, never by its arithmetic sign.

### Directing attention on the graph

This is where the book is most specific, and where most of the work went.

**Grey is the base; one colour is the signal.** Contrast only works when it is scarce, so
everything the headline does not argue about recedes — real data or not. On the two market
charts only *Mainstream* carries hue; Category, Economy and Premium are grey. On the cost
chart COBALT is grey, because a €0.5m increase drawn in the adverse colour became the loudest
mark on a page whose entire claim is that spend came *down* — and spending more behind a
growing brand is not adverse in the first place.

**Grey the labels too, not just the mark.** A bold black number beside a muted bar pulls the
eye straight back to the row you just muted. The muted rows recede on weight and size while
staying legible: de-emphasised *text* is `#595959`, because the paler greys used for *fills*
fall below readable contrast on white.

**Declutter, then keep the one thing that earns its place.** No gridlines anywhere. No value
axis when every mark carries its own label. But the converse matters just as much: when the
monthly line chart dropped its data labels for the seven quiet H1 months, the value axis came
back with them, because a reader now has no other way to recover those values.

**Colour never carries direction alone.** Roughly one in twelve men cannot separate the two
poles, so every chart pairs colour with a printed sign, and positive bars add a hatch.

**Do not distort length.** Bars are read from zero, always. The linter caught a truncated
axis on the monthly chart during this build — the shaded gap is the subject of that chart,
and starting the axis at €2.5m drew it roughly twice its true size. Zero-basing it costs the
lower third of the canvas, and the callout moved into the space instead.

**Annotate, do not animate.** The pack has to work for people who were not in the room, so
there are no build-ups or reveals. Every chart states its own point in text on the page, and
the PDF prints the narration the PPTX keeps in speaker notes.

> The Markdown conversion of the book and its extracted images are kept locally in
> `references/domain/` and **are not committed**, for copyright reasons.

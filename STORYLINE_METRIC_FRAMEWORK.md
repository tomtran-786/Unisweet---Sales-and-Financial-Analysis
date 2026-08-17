# UniSweet - Storyline and Metric Framework

## 1. Purpose and management question

This document translates the available Market, Sales and P&L data into a four-page management narrative for FY2024 performance.

> **Topline and market share deteriorated, while PBO increased because lower marketing expenditure more than offset the decline in Gross Profit. The management task is therefore to restore profitable growth without giving back the protected profit.**

The storyline follows one decision path:

```text
How serious is the slowdown?
-> Where is value and share being lost?
-> Which customers, products and commercial levers explain the gap?
-> Why did PBO still grow?
-> Which three actions can restore profitable growth?
```

The narrative uses balanced tension: the profit result is acknowledged, but it is not presented as evidence that the underlying business is healthy.

---

## 2. Reporting convention and source boundaries

| Source | Narrative use | Actual grain / period |
|---|---|---|
| `outputs/sales_master.csv` | FY2024 versus FY2023 Sales headlines and drivers | Month x Customer x Brand x Pack Type x Pack Size |
| `inputs/pnl/P&L Table.xlsx` | Profitability, cost and PBO bridge | Brand x Year |
| `inputs/market/Market Report MAT Nov'24.xlsx` | Category, value growth and value-share context | MAT period x Channel x Segment x Manufacturer x Brand |

### 2.1 Raw/P&L-aligned headline base

All FY2024 and FY2023 Sales rows are included in the narrative base:

```text
Narrative Sales Base = all rows in outputs/sales_master.csv
Headline Period = FY2024 versus FY2023
```

This base reconciles exactly to the P&L at Total and Brand level:

| Metric (kEUR) | Raw Sales FY2023 | P&L FY2023 | Raw Sales FY2024 | P&L FY2024 |
|---|---:|---:|---:|---:|
| GSV | 371,528.3 | 371,528.3 | 349,247.6 | 349,247.6 |
| Discount | 81,461.4 | 81,461.4 | 78,743.3 | 78,743.3 |
| Turnover | 290,066.9 | 290,066.9 | 270,504.3 | 270,504.3 |

The raw base includes rows flagged `TO > GSV`. These rows contribute 2,574.5 kEUR of FY2023 TO and 3,173.0 kEUR of FY2024 TO and remain subject to business validation. They are retained here solely because management selected the P&L-aligned reporting base.

### 2.2 Certified analytical base remains separate

`scripts/metrics.py` continues to use `certified_for_analysis = True`. It is not changed by this narrative update and must not be used as the source for the raw/P&L-aligned headline values in this document.

Use the certified view only as a data-quality sensitivity until the flagged rows have been resolved.

### 2.3 Units, periods and FX

- Sales and P&L values are treated as kEUR, consistent with the case brief and the exact Sales-to-P&L reconciliation. Slide-ready values are shown as EUR millions.
- Market values are mEUR and use MAT Nov'24 versus MAT-1.
- Sales and P&L use calendar FY2024 versus FY2023. Market MAT results must not be presented as the same time period.
- The case brief specifies 26,723 VND/EUR; the P&L workbook uses 26,743. Use 26,723 for any brief-required conversion pending reconciliation, and keep the core storyline in kEUR/EUR millions.
- The P&L workbook header says "in EUR" while the case brief says kEUR. Because the values reconcile to the Sales kEUR data, the narrative applies the kEUR interpretation and flags the workbook label for correction.

---

## 3. Four-page management storyline

### Page 1 - Executive truth

#### Slide headline

> **Topline decelerated, but PBO grew - growth quality is the real issue.**

#### Evidence

| Metric | FY2023 | FY2024 | Movement |
|---|---:|---:|---:|
| GSV | EUR371.5m | EUR349.2m | -EUR22.3m / -6.0% |
| Turnover | EUR290.1m | EUR270.5m | -EUR19.6m / -6.7% |
| Discount/GSV | 21.93% | 22.55% | +62 bps |
| Gross Profit | EUR138.7m | EUR128.4m | -EUR10.3m / -7.4% |
| Gross Margin | 47.82% | 47.47% | -35 bps |
| Marketing Expense | EUR58.0m | EUR42.5m | -EUR15.5m / -26.7% |
| PBO | EUR80.7m | EUR85.9m | +EUR5.2m / +6.4% |
| PBO Margin | 27.83% | 31.76% | +393 bps |

#### Management interpretation

- The business is not merely converting less GSV into TO; GSV itself declined 6.0%, showing that the slowdown is broader than discount intensity.
- Discount/GSV increased 62 bps. Holding the FY2023 rate on FY2024 GSV gives an arithmetic counterfactual of approximately EUR2.17m of additional TO, equivalent to about 11% of the reported TO decline.
- This counterfactual is a diagnostic, not a causal promotion-ROI estimate. Most of the EUR19.6m TO gap remains associated with the lower GSV base.
- PBO growth is cost-led rather than growth-led: the EUR15.5m marketing reduction more than offset the EUR10.3m Gross Profit decline.

#### Recommended visual

A compact scorecard plus a bridge from GSV to TO and from Gross Profit to PBO. Do not present the positive PBO result without the declining GSV, TO and Gross Profit context.

---

### Page 2 - Market diagnosis

#### Slide headline

> **Share loss is concentrated in OLIVE-Mainstream, with MT as the strategic hotspot.**

#### Category and UniSweet performance

| MAT Nov'24 view | MAT-1 | MAT | Movement |
|---|---:|---:|---:|
| Category Sales Value | EUR459.0m | EUR453.0m | -EUR6.0m / -1.3% |
| UniSweet Sales Value | EUR296.7m | EUR283.9m | -EUR12.8m / -4.3% |
| UniSweet Value Share | 64.65% | 62.68% | -1.97 points |

The category decline explains a market headwind, but it does not explain the share loss. UniSweet lost share because its value declined faster than the category.

#### Brand share bridge

| UniSweet brand | Value growth | Share movement | Interpretation |
|---|---:|---:|---|
| OLIVE / Mainstream | -6.9% | -2.98 points | Source of the company share loss |
| SKY / Economy | +23.8% | +0.45 points | Partial offset |
| COBALT / Premium | +3.9% | +0.56 points | Partial offset |

OLIVE's -2.98-point movement was partly offset by approximately +1.01 points from SKY and COBALT, leaving the UniSweet total at -1.97 points.

#### Channel diagnosis

| Channel | Category growth | UniSweet growth | UniSweet share movement | Main competitive signal |
|---|---:|---:|---:|---|
| DT | -1.3% | -1.7% | -0.28 points | NAVY gained +0.84 points |
| MT | -1.3% | -10.2% | -6.07 points | LILAC gained +5.53 points |

- OLIVE-MT declined 16.7% in market value and lost 7.88 share points.
- MT is the strategic relative-performance hotspot. Internal MT TO declined 10.0%, versus 5.7% in DT.
- DT still created the larger absolute internal TO gap: -EUR12.44m versus -EUR7.12m in MT. Management should not equate the MT hotspot with the largest absolute value gap.
- Competitive threats are channel-specific: LILAC is the major observed MT threat, while NAVY gained in DT but declined in MT.

#### Interpretation guardrail

The Market file does not provide complete segment totals. It supports statements about the listed brands and their category value share, but it does not support a standalone claim that the entire Mainstream segment declined.

#### Recommended visual

A value-share bridge by UniSweet brand, paired with an MT-versus-DT comparison. Highlight OLIVE-MT and label the different competitor threat in each channel.

---

### Page 3 - Sales drivers

#### Slide headline

> **The decline is an existing-customer and SKU issue, not broad customer attrition - and it accelerated sharply in H2.**

#### Where the TO gap occurred

| Driver lens | FY2024 TO change | Share of company decline / interpretation |
|---|---:|---|
| OLIVE | -EUR16.63m | 85% of the company decline |
| SKY | -EUR3.91m | Additional drag |
| COBALT | +EUR0.97m | Partial offset |
| DT | -EUR12.44m | Largest absolute channel gap |
| MT | -EUR7.12m | Faster relative decline |
| OLIVE-DT | -EUR8.72m | Largest Brand-Channel absolute gap |
| OLIVE-MT | -EUR7.91m | Most acute Brand-Channel growth rate at -14.9% |

#### Timing

- H2 accounted for -EUR18.72m, or approximately 96% of the full-year TO decline.
- February was the largest monthly gap at -EUR7.48m.
- Weakness became sustained from September through December, contributing a combined -EUR15.67m.
- The monthly pattern is evidence of volatility and H2 deterioration. Monthly sell-in data alone does not establish a holiday or seasonal cause.

#### Customer concentration

| Customer | Channel | FY2024 TO change | Growth |
|---|---|---:|---:|
| Bliss | MT | -EUR6.89m | -36.0% |
| Candies | DT | -EUR6.47m | -15.2% |
| Macarons | MT | -EUR4.35m | -25.7% |

Together, Bliss, Candies and Macarons contributed -EUR17.72m, equivalent to 91% of the company decline.

Active customers moved only from 19 to 18. The only observed full-year exit was Treats, representing approximately 0.5 kEUR of TO. The commercial problem is therefore lower spend at existing large customers, not meaningful customer attrition.

#### Product concentration and offsets

| Product | FY2024 TO change | Growth |
|---|---:|---:|
| POUCH 900GR | -EUR13.04m | -12.8% |
| PACK 1.1KG | -EUR10.50m | -10.9% |
| POUCH 100GR | -EUR3.94m | -40.6% |
| PACK 250GR | -EUR2.29m | -3.5% |
| POUCH 400GR | +EUR6.04m | +49.2% |
| BAR 50GR | +EUR2.14m | +793.0% from a small base |
| BOTTLE 1KG | +EUR1.55m | +105.7% |

The two largest declining formats exceed the total company decline because growing formats and COBALT offset part of the loss.

#### Customer x SKU evidence and discount diagnostics

The priority is the intersection of the declining customers and packs, rather than a broad customer or portfolio-wide discount response:

| Priority customer x brand x SKU | FY2024 TO change |
|---|---:|
| Bliss x OLIVE x POUCH 900GR | -EUR5.65m |
| Macarons x OLIVE x POUCH 900GR | -EUR2.66m |
| Candies x OLIVE x PACK 1.1KG | -EUR3.21m |

- POUCH 900GR combined a -12.8% TO decline with a +103 bps increase in Discount/GSV.
- Bliss combined a -36.0% TO decline with a +99 bps increase in Discount/GSV.
- Candies combined a -15.2% TO decline with a +45 bps increase in Discount/GSV.
- Macarons declined 25.7% even though Discount/GSV improved by 83 bps. Discount is therefore not a sufficient explanation or recovery lever on its own.

#### Recommended visual

A driver tree from Brand -> Channel -> Customer -> SKU, with a monthly TO-change strip below it. Use discount rate only as a diagnostic overlay, not as proof of promotion effectiveness.

---

### Page 4 - Profit bridge and strategic actions

#### Slide headline

> **Protect PBO while selectively reinvesting to restore profitable growth.**

#### PBO bridge

```text
Gross Profit change                 -EUR10.30m
Less: Marketing Expense change     -EUR15.50m
------------------------------------------------
PBO change                           +EUR5.20m
```

Marketing Expense decreased from EUR58.0m to EUR42.5m. This reduction protected PBO, but it does not demonstrate that the underlying growth model improved.

Total Supply Chain Cost declined by EUR9.26m in absolute terms, but Supply Chain Cost/TO increased from 52.18% to 52.53%, a deterioration of approximately 35 bps. The correct conclusion is lower expenditure on a smaller sales base, not improved supply-chain efficiency.

#### Portfolio context

- **OLIVE:** TO -7.3%, GM -100 bps and PBO +6.6%, with the PBO result protected by a 30% marketing reduction.
- **COBALT:** TO +11.6%, GM +100 bps and PBO +4.7%; market value also grew 3.9% and share gained 0.56 points. COBALT is the clearest scalable growth proof point.
- **SKY:** internal TO declined 7.4%, while market value grew 23.8% and share gained 0.45 points. This divergence is a diagnostic opportunity, not evidence of a confirmed sell-in/sell-out problem until period, inventory and distribution data are reconciled.

#### Three strategic actions

| Action | Immediate focus | Management outcome |
|---|---|---|
| 1. OLIVE-MT Customer x SKU Recovery | Bliss, Macarons, POUCH 900GR and PACK 1.1KG; parallel DT root-cause review for Candies | Recover profitable TO at the points of highest value loss |
| 2. Trade-Spend and Discount ROI Reset | Customer- and SKU-level incrementality, discount ceilings and contribution guardrails | Stop paying more where sales and margin do not respond |
| 3. Selective Reinvestment with Profit Guardrails | Ring-fence part of marketing savings; scale COBALT; diagnose SKY divergence | Restore growth without giving back protected PBO |

The detailed owners, timing, KPIs, decision gates and data requirements are defined in `references/domain/calls-to-action-by-audience.md`.

#### Recommended visual

A Gross Profit-to-PBO bridge followed by three action cards. Each action card should state the owner, first decision gate, KPI and evidence required to scale.

---

## 4. Metric framework

### 4.1 Sales value metrics

```text
GSV = SUM(gsv_keur)
TO = SUM(turnover_keur)
Discount = GSV - TO = SUM(discount_keur)
Absolute Change = Current - Prior
Growth % = Current / Prior - 1
```

Supported cuts:

- Total
- Brand
- Channel
- Brand x Channel
- Customer
- Exact Product
- Pack Type and Pack Size

### 4.2 Driver contribution

```text
Entity TO Change = Entity TO Current - Entity TO Prior
Change Contribution % = Entity TO Change / Total TO Change
```

Calculate contributions separately by Brand, Channel, Customer and Product. Do not add contributions across dimensions because each dimension independently explains the same total change.

### 4.3 Mix and active customers

```text
Product TO Mix % = Product TO / Total TO
Brand-Product Mix % = Brand x Product TO / Total Brand TO
Active Customer = Customer with full-year aggregated TO > 0
```

Active customer counts describe customers present in the internal dataset, not market distribution. Pack Size identifies a format; it must not be used to infer physical volume or weight sold.

### 4.4 Discount and Gross-to-Net

```text
Discount % GSV = SUM(Discount) / SUM(GSV)
Discount % TO = SUM(Discount) / SUM(TO)
Rate Movement bps = (Current Rate - Prior Rate) x 10,000
```

Never average row-level discount percentages. Promotion effectiveness cannot be inferred from discount rates alone; it requires incremental sales, baseline, timing and margin data.

### 4.5 Monthly comparison

Compare each FY2024 month with the same FY2023 month using monthly levels, not cumulative YTD values. Monthly measures may include TO, GSV, Discount, Discount/GSV and active customers.

Use the series to identify timing and volatility. Do not label a pattern as seasonal or holiday-driven without weekly history or multiple comparable years.

### 4.6 P&L metrics

```text
Gross Profit = TO - Total Supply Chain Cost
Gross Margin % = Gross Profit / TO
PBO = Gross Profit - Marketing Expense
PBO Margin % = PBO / TO
PBO Change = Gross Profit Change - Marketing Expense Change
```

P&L is available only at Brand, Total and Year grain. Do not allocate Gross Profit, Supply Chain Cost, Marketing Expense or PBO to Customer, Channel or Product without an approved allocation model.

### 4.7 Market metrics

```text
Market Value Growth % = Sales Value MAT / Sales Value MAT-1 - 1
Sales Value Movement = Sales Value MAT - Sales Value MAT-1
Value Share Movement pp = Value Share MAT - Value Share MAT-1
```

Use the source Gain/Loss columns as reconciliation checks. Keep Total, MT and DT separate, and do not compare MAT market values directly with FY internal Sales values as if they shared one reporting period.

---

## 5. Interpretation guardrails

1. **Raw data does not mean validated data.** The raw base is used because it reconciles to P&L; `TO > GSV` rows still require resolution.
2. **Discount movement is not promotion causality.** The EUR2.17m counterfactual is arithmetic, not a measured ROI result.
3. **A smaller market does not cause share loss.** Share fell because UniSweet declined faster than the category.
4. **MT is the relative hotspot; DT is the larger absolute gap.** Both statements must remain visible.
5. **Customer concentration is not customer attrition.** The decline is concentrated in spend at existing large accounts.
6. **Monthly weakness is not proof of holiday seasonality.** Additional weekly POS, promotion, inventory and OOS data are required.
7. **Lower absolute cost is not automatically efficiency.** Supply-chain efficiency must be assessed using cost rate and service levels.
8. **PBO resilience may not be sustainable.** Marketing reductions protected profit, but the available data does not prove whether lower investment caused the sales or share decline.
9. **SKY's internal/market divergence is a question, not a conclusion.** Reconcile sell-in, market measurement, inventory, timing and distribution before acting.

---

## 6. Source references

- Internal Sales: `outputs/sales_master.csv`
- P&L: `inputs/pnl/P&L Table.xlsx`, sheet `PnL table`
- Market: `inputs/market/Market Report MAT Nov'24.xlsx`, sheet `Market Data`
- Case brief: `references/source-briefs/SEO-V Finance Business Partner Case Study.pdf`
- Detailed actions: `references/domain/calls-to-action-by-audience.md`

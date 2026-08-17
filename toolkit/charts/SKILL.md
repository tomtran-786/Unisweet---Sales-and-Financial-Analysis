---
name: storytelling-with-data
description: Build, declutter and lint executive business charts in matplotlib - bar, horizontal bar, line, slopegraph, waterfall, heatmap and big-number visuals with action titles, direct labels and a grey/one-accent palette. Use when asked to chart, graph, plot, visualise or redesign data, build an exec chart or KPI visual, fix a cluttered or misleading chart, choose a chart type, or check a chart before it goes in a deck or report.
---

# Storytelling with data

Chart helpers and a linter that encode the method from Cole Nussbaumer Knaflic,
*Storytelling with Data* (Wiley, 2015), sourced from
`references/domain/storytelling-with-data-p1.md`.

Two files do the work. **Paths below are relative to the repo root.**

| File | What it is |
|---|---|
| `toolkit/charts/swd.py` | The driver. matplotlib helpers for the seven chart forms the book recommends. |
| `toolkit/charts/lint.py` | The gate. Fails charts on the specific defects the book demonstrates. |
| `toolkit/charts/demo.py` | One worked example of every form, built from this repo's real data. |
| `toolkit/charts/gallery/` | The rendered output of `demo.py`. Look here before designing. |

This is the **matplotlib / static-export** path, for charts that end up in a
deck, a PDF or a PNG. For charts rendered as HTML, React or an Artifact, use
the separate bundled `dataviz` skill instead.

## Prerequisites

Already satisfied in this repo — `pip install -r requirements.txt` covers it.
Verified present on this machine: matplotlib 3.9.2, Arial (macOS ships it at
`/System/Library/Fonts/Supplemental/Arial.ttf`).

`swd.py` falls back through Helvetica → Liberation Sans → DejaVu Sans. Only
Liberation Sans is metric-compatible with Arial, so on a machine without
Arial install the `fonts-liberation` package before trusting how text fits.
(Unverified here — this repo runs on macOS.)

## Run (agent path)

Build the gallery and confirm the toolchain works:

```bash
cd toolkit/charts && python3 demo.py
```

Lint any script that builds figures. Exit code is 1 if there are errors:

```bash
cd toolkit/charts && python3 lint.py demo.py
```

Confirm the linter still bites (must report 4 errors / 10 warnings):

```bash
cd toolkit/charts && python3 lint.py bad_examples.py
```

Use it as a library from anywhere in the repo:

```bash
PYTHONPATH=toolkit/charts python3 -c "
import swd, lint
swd.use()
fig, ax = swd.figure('Three customers explain 91% of the decline',
                     subtitle='Change in turnover, EURm',
                     source='Source: outputs/sales_master.csv')
swd.hbar(ax, ['Bliss','Candies','Macarons','Others'], [-6.9,-6.5,-4.4,-1.8],
         highlight={'Bliss','Candies','Macarons'}, sort=True)
print(lint.check(fig) or 'clean')
fig.savefig('/tmp/chart.png', bbox_inches='tight')
"
```

Then **open the PNG and look at it.** The linter checks structure, not whether
two labels overlap.

## Palette

Grey is the base, one colour is the signal. Contrast only works when it is
scarce, so the greys below are doing the most important job on the page.

| Constant | Hex | Use |
|---|---|---|
| `INK` | `#262626` | titles and text that must be read |
| `GREY` | `#595959` | subtitles, secondary text |
| `BASE` | `#8c8c8c` | data that is context, not signal |
| `MUTED` | `#bfbfbf` | axis lines, tick labels, de-emphasised data |
| `ACCENT` | `#004c6d` | the one "look here" colour; also favourable movement |
| `ACCENT_2` | `#f79545` | the adverse pole, when a story has two |

When one accent is genuinely not enough — a sequence to rank, or a signed
matrix — use the two ramps rather than inventing colours:

```python
SEQ_BLUE   = ("#004c6d", "#346888", "#5886a5", "#7aa6c2", "#9dc6e0", "#c1e7ff")
SEQ_ORANGE = ("#f79545", "#faa35e", "#fdb177", "#ffbf8f", "#ffcda8", "#ffdbc1")
```

**Blue marks favourable movement; orange marks adverse.** Favourable means good
for the business, which is *not* the same as a positive number — a €15.5m cut
in marketing spend is blue even though it prints as `-15.5`. Decide by what the
number means, never by its sign. Within each ramp the darkest step is the
signal and `#9dc6e0`/`#c1e7ff` (or `#fdb177`/`#ffdbc1`) carry context.

The corollary for a diverging scale: the adverse pole depends on the metric.
Falling turnover is adverse, but a *rising* discount rate is too, so two panels
of the same figure may need opposite poles of the same ramp.

`sequential_cmap()` returns the blue ramp light→dark for a heatmap that ranks.
`diverging_cmap(low, high)` returns a two-pole ramp through white — pass the
poles explicitly so the adverse side matches the metric.

**Contrast:** no step of `SEQ_ORANGE` reaches 4.5:1 against white or against
its own pale tint (`#f79545` manages 2.3:1). Orange is a fill and mark colour
only; text sitting on or beside an orange fill is `INK`. Blue is dark enough to
take white text at `#004c6d`/`#346888`.

Keep saturated hues to four or fewer per chart, and never let colour carry
direction on its own — roughly 8% of men cannot separate the two poles. Every
chart in this repo pairs colour with a printed sign, and bars add a hatch on
the positive side.

**Spend hue only on what the headline argues about.** Everything else is grey,
even when it is real data. In practice that means:

| Grey this | Why |
|---|---|
| Waterfall opening/closing totals | The tallest shapes on the page, but only the frame — the steps between them are the story |
| A "Net" or summary bar | A sum of the bars beside it, not a new fact. Keep its *label* bold if it is the headline number |
| "All other (net)" residuals | The share the headline explicitly sets aside |
| The half of a time series the headline is not about | If the claim is "96% of the decline was in H2", H1 is background |
| Rows the headline does not name | In a three-brand comparison naming two, the third is the backdrop |
| Rounding artefacts and reconciliation noise | Kept for transparency, never for attention |
| The source/caveat line | Provenance, not argument — `MUTED`, the faintest thing on the page |

Grey the tick label and the value label too, not just the mark — a bold black
number next to a grey bar pulls the eye straight back to what you just muted.

## Layout

- **No gridlines.** Not light ones, not dashed ones. `swd.use()` sets
  `axes.grid: False` and `declutter()` calls `ax.grid(False)`; leave both alone.
  If a reader needs to recover a value, label the mark directly.
- **Drop the value axis once every mark is labelled.** Ticks that repeat what
  the direct labels already say are the same clutter as gridlines. Keep the
  zero line (`axhline`/`axvline` in `MUTED`) — that is a reference, not a grid.
- **One left edge.** Title, subtitle, annotations and source line all sit at
  `x=0.08`, because the eye reads a page as a Z: in at top-left, right across
  the title, diagonally down through the plot, then right along the source.
  Each sweep should start from the same edge. `swd.figure()` and `footnote()`
  already do this; `annotate()` defaults to `ha="left"` for the same reason.
- **Exception: labels attached to a mark.** Bar-end values, waterfall step
  labels, heatmap cell values and line end-labels stay anchored to the thing
  they name. Proximity is what identifies them; moving them to the page edge
  breaks the pairing. Left-align the *words*, not the *numbers on the data*.

## Choosing the form

| You have | Use | Call |
|---|---|---|
| One or two numbers | the number itself, not a chart | `swd.bignum` |
| Categories, esp. long names | horizontal bar (the default choice) | `swd.hbar` |
| Categories over a few time buckets | vertical bar | `swd.bar` |
| Continuous data, consistent intervals | line, labelled at the end | `swd.line` |
| Two time points, several categories | slopegraph | `swd.slopegraph` |
| Start, increments, end | waterfall | `swd.waterfall` |
| A table you want to keep, plus a cue | heatmap, one hue | `swd.heatmap` |

Not implemented, on purpose: pie, donut, 3-D, secondary y-axis. `lint.py`
errors on all four.

## Before you draw

Answer these three, in this order, or the chart has nothing to be right about.
Full worksheet in `reference/planning.md`.

1. **Who** is the single decision maker? (Not "stakeholders".)
2. **What** do you need them to do? Write it as a verb.
3. **How** does the data support it? Data is evidence for the ask, not the ask.

Then write the **action title first** — the takeaway as a full claim
("Three customers explain 91% of the decline"), never the topic
("Customer Analysis"). `swd.figure()` refuses to build without one, and
`lint.py` warns when a title reads as a topic.

## Gotchas

These cost real debugging time in this repo:

- **`lint.py` runs your script with `runpy`, so figures must be built at import
  time.** `demo.py` calls `main()` at module level for exactly this reason. Put
  chart building behind `if __name__ == "__main__":` and the linter silently
  reports zero figures and passes.
- **Colour direction and the printed number must encode the same thing.**
  Negating values to make "darker = bigger loss" also flips every data label:
  a 7.5m *loss* prints as `+7.5`. Colour by magnitude and label with the true
  signed value, or pick a metric where dark = high is already the story.
- **Action titles get fact-checked, and they are the one thing nobody
  re-derives.** A draft title here said "fell below prior year from July";
  July was in fact *above*. Verify the claim against the data before shipping.
- **`swd.annotate` takes data coordinates, not axes fractions.** Aim it at
  visible whitespace; an annotation at a bar's midpoint runs off the canvas.
- **`highlight=` takes labels, not indices** — `{"Bliss"}`, not `{0}`.
- **Direct labels need headroom at both ends.** `_enforce_zero` pads both
  sides by 12% because which end a label sits on depends on each bar's sign.
  All-negative data collided with the tick labels before this.
- **Call `swd.use()` once before `swd.figure()`** — it installs the font stack
  and strips gridlines/spines via rcParams.
- **Slopegraphs and line charts legitimately have no zero baseline.** They
  encode position, not length. The linter only enforces zero on bar rectangles.
- Backend is forced to `Agg`. Never call `plt.show()`.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `lint.py` says "0 figure(s)" and passes | Figures built under `if __name__ == "__main__"`. Build at module level. |
| `FileNotFoundError` on `outputs/report_visuals/data/...` | `demo.py` resolves the repo root as `Path(__file__).parents[2]`. It needs the exported chart data from `visualisations.ipynb`. |
| `findfont: Font family 'Arial' not found` | matplotlib silently substitutes DejaVu Sans, which has different widths. Install `fonts-liberation`. |
| Value labels overlap category labels | Data is all one sign; confirm `_enforce_zero` ran (it pads both ends). |
| `ValueError: figure() requires an action title` | Working as designed. Write the takeaway. |

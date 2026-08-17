"""Storytelling-with-Data chart helpers for matplotlib.

Encodes the six lessons from Cole Nussbaumer Knaflic, *Storytelling with Data*
(Wiley, 2015) as callable code rather than advice:

  1. context      -> figure() forces an action title; caller supplies audience/ask
  2. visual       -> only the chart types the book actually recommends
  3. declutter    -> no border, no gridlines, no tick marks, no trailing zeros
  4. attention    -> everything grey, one accent; `highlight=` selects the signal
  5. design       -> direct labels instead of legends, left-aligned text, footnote
  6. story        -> annotate() for the words that carry the "so what"

Deliberately absent: pie, donut, 3-D, secondary y-axis. lint.py fails the build
if they reappear.

Usage:
    import swd
    fig, ax = swd.figure("Bliss and Macarons drive the decline",
                         subtitle="FY2024 vs FY2023 turnover change, EURm",
                         source="outputs/sales_master.csv")
    swd.hbar(ax, labels, values, highlight={"Bliss", "Macarons"})
    fig.savefig("chart.png")
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb

__all__ = [
    "GREY", "BASE", "MUTED", "ACCENT", "ACCENT_2", "INK",
    "SEQ_BLUE", "SEQ_ORANGE", "sequential_cmap", "diverging_cmap",
    "use", "figure", "bignum", "hbar", "bar", "line", "slopegraph",
    "waterfall", "heatmap", "annotate", "footnote", "declutter", "money",
]

# --- palette -----------------------------------------------------------------
# The book's core move: base everything in grey, spend one colour on the signal.
# Grey (not black) as the base leaves more contrast headroom for the accent.
INK = "#262626"      # titles and other text that must be read
BASE = "#8c8c8c"     # data that is context, not signal
MUTED = "#bfbfbf"    # axis lines, tick labels, de-emphasised data
GREY = "#595959"     # subtitles, secondary text
ACCENT = "#004c6d"   # the one "look here" colour - also: favourable movement
ACCENT_2 = "#f79545" # second pole, for adverse movement (fills and marks only)

# Two muted ramps for the cases a single accent cannot cover: saturation of one
# hue to rank a sequence, and one opposing hue for the other pole. BLUE MARKS
# FAVOURABLE MOVEMENT, ORANGE MARKS ADVERSE. Favourable means good for the
# business, which is not always a positive number - a cut in cost is blue.
# Never let either ramp carry direction on its own; add a sign or a hatch.
#
# Contrast: no step of SEQ_ORANGE reaches 4.5:1 against white or against its
# own pale tint (#f79545 manages 2.3:1). Orange is a fill and mark colour;
# text on or beside an orange fill is INK.
SEQ_BLUE = ("#004c6d", "#346888", "#5886a5", "#7aa6c2", "#9dc6e0", "#c1e7ff")
SEQ_ORANGE = ("#f79545", "#faa35e", "#fdb177", "#ffbf8f", "#ffcda8", "#ffdbc1")

_FONT_STACK = ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"]


def sequential_cmap(ramp=SEQ_BLUE):
    """Light -> dark saturation of one hue. Saturation can rank; a rainbow cannot."""
    return LinearSegmentedColormap.from_list("swd_seq", list(reversed(ramp)))


def diverging_cmap(low: str = SEQ_ORANGE[0], mid: str = "#ffffff",
                   high: str = SEQ_BLUE[0]):
    """Two poles through a neutral centre, for signed data with a real zero."""
    return LinearSegmentedColormap.from_list("swd_div", [low, mid, high])


def use(accent: str = ACCENT, font_size: float = 11.0) -> None:
    """Install the decluttered defaults globally. Call once per script."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": _FONT_STACK,
        "font.size": font_size,
        "text.color": INK,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": GREY,
        "axes.linewidth": 0.8,
        "axes.grid": False,            # lesson 3: gridlines compete with data
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.prop_cycle": plt.cycler(color=[accent, BASE, MUTED, GREY]),
        "xtick.color": GREY,
        "ytick.color": GREY,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "legend.frameon": False,       # lesson 5: prefer direct labels entirely
    })


def _grey_or(colour: str, is_signal: bool, base: str = BASE) -> str:
    return colour if is_signal else base


def money(v: float, unit: str = "", decimals: int = 1, signed: bool = False) -> str:
    """Format a number without the trailing zeros the book calls a pet peeve."""
    s = f"{v:,.{decimals}f}"
    if decimals and s.rstrip("0").rstrip(".") != s:
        s = s.rstrip("0").rstrip(".")
    if signed and v > 0:
        s = "+" + s
    return f"{s}{unit}"


# --- canvas ------------------------------------------------------------------
def figure(title: str,
           subtitle: str | None = None,
           source: str | None = None,
           figsize: tuple[float, float] = (12.8, 7.2),
           dpi: int = 150):
    """A figure whose title slot is reserved for an ACTION title.

    `title` should state the takeaway ("Estimated 2025 spending is above
    budget"), never the topic ("2025 budget").

    Every text element here shares one left edge at x=0.08. The eye reads a
    page as a Z: it enters top-left, sweeps right across the title, drops
    diagonally through the plot, then sweeps right again along the source line.
    A common left edge is what makes each of those sweeps start in the same
    place. Centred text creates no edge to start from.
    """
    if not title or not title.strip():
        raise ValueError("figure() requires an action title - the takeaway, not the topic")

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    # Room at the top for title/subtitle, at the bottom for the source line.
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.08, right=0.94)

    fig.text(0.08, 0.945, title, ha="left", va="top",
             fontsize=plt.rcParams["font.size"] * 1.75, fontweight="bold", color=INK)
    if subtitle:
        fig.text(0.08, 0.875, subtitle, ha="left", va="top",
                 fontsize=plt.rcParams["font.size"] * 1.05, color=GREY)
    if source:
        footnote(fig, source)
    return fig, ax


def footnote(fig, text: str) -> None:
    """Source / caveat line: present, but pushed to the background."""
    fig.text(0.08, 0.035, text, ha="left", va="bottom",
             fontsize=plt.rcParams["font.size"] * 0.8, color=MUTED)


def declutter(ax, keep_x: bool = True, keep_y: bool = False) -> None:
    """Strip the elements that cost cognitive load and return nothing."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_visible(keep_y)
    ax.spines["bottom"].set_visible(keep_x)
    ax.tick_params(length=0)
    ax.grid(False)
    if not keep_y:
        ax.set_yticks([])
    if not keep_x:
        ax.set_xticks([])


# --- simple text -------------------------------------------------------------
def bignum(ax, number: str, caption: str, accent: str = ACCENT) -> None:
    """Lesson 2: one or two numbers do not need a chart. Use the number."""
    ax.axis("off")
    ax.text(0.0, 0.62, number, ha="left", va="center",
            fontsize=plt.rcParams["font.size"] * 6.0, fontweight="bold", color=accent)
    ax.text(0.0, 0.26, caption, ha="left", va="center",
            fontsize=plt.rcParams["font.size"] * 1.3, color=GREY, wrap=True)


# --- bars --------------------------------------------------------------------
def hbar(ax, labels, values, highlight=None, accent: str = ACCENT,
         unit: str = "", decimals: int = 1, sort: bool = False) -> None:
    """The book's go-to for categorical data: names read before the data.

    `highlight` is a set/list of labels to render in the accent colour;
    everything else goes grey. Bars are labelled directly, so no legend and
    no value axis.
    """
    highlight = set(highlight or ())
    pairs = list(zip(labels, values))
    if sort:
        pairs.sort(key=lambda p: p[1])
    labels = [p[0] for p in pairs]
    values = [p[1] for p in pairs]

    ypos = range(len(labels))
    colours = [_grey_or(accent, lab in highlight) for lab in labels]
    ax.barh(list(ypos), values, color=colours, height=0.68)  # bars wider than gaps

    ax.set_yticks(list(ypos))
    ax.set_yticklabels(labels)
    for tick, lab in zip(ax.get_yticklabels(), labels):
        if lab in highlight:
            tick.set_color(INK)
            tick.set_fontweight("bold")
        else:
            tick.set_color(GREY)

    _enforce_zero(ax, axis="x", values=values)
    span = max(max(values, default=0), 0) - min(min(values, default=0), 0)
    pad = span * 0.012 if span else 0.1
    for y, v, lab in zip(ypos, values, labels):
        ax.text(v + (pad if v >= 0 else -pad), y, money(v, unit, decimals),
                va="center", ha="left" if v >= 0 else "right",
                color=INK if lab in highlight else GREY,
                fontweight="bold" if lab in highlight else "normal")

    ax.invert_yaxis()
    declutter(ax, keep_x=False, keep_y=False)
    ax.set_yticks(list(ypos))
    ax.set_yticklabels(labels)
    ax.tick_params(length=0)


def bar(ax, labels, values, highlight=None, accent: str = ACCENT,
        unit: str = "", decimals: int = 1) -> None:
    """Vertical bars. Zero baseline is enforced, not suggested."""
    highlight = set(highlight or ())
    xpos = range(len(labels))
    colours = [_grey_or(accent, lab in highlight) for lab in labels]
    ax.bar(list(xpos), values, color=colours, width=0.68)

    ax.set_xticks(list(xpos))
    ax.set_xticklabels(labels, rotation=0)  # never diagonal: 52% slower to read
    _enforce_zero(ax, axis="y", values=values)

    span = max(max(values, default=0), 0) - min(min(values, default=0), 0)
    pad = span * 0.02 if span else 0.1
    for x, v, lab in zip(xpos, values, labels):
        ax.text(x, v + (pad if v >= 0 else -pad), money(v, unit, decimals),
                ha="center", va="bottom" if v >= 0 else "top",
                color=INK if lab in highlight else GREY,
                fontweight="bold" if lab in highlight else "normal")
    declutter(ax, keep_x=True, keep_y=False)


def _enforce_zero(ax, axis: str, values) -> None:
    """Bar length encodes magnitude, so the value axis must contain zero."""
    lo, hi = (min(values, default=0), max(values, default=0))
    lo, hi = min(lo, 0), max(hi, 0)
    span = hi - lo or 1.0
    # Headroom on BOTH ends: direct labels sit outside the bar end, and which
    # end that is depends on the sign of each bar.
    lo, hi = lo - span * 0.12, hi + span * 0.12
    if axis == "y":
        ax.set_ylim(lo, hi)
        ax.axhline(0, color=MUTED, linewidth=0.8)
    else:
        ax.set_xlim(lo, hi)
        ax.axvline(0, color=MUTED, linewidth=0.8)


def waterfall(ax, labels, deltas, start: float, start_label: str = "Start",
              end_label: str = "End", accent: str = ACCENT,
              accent_down: str = BASE, unit: str = "", decimals: int = 1) -> None:
    """Start -> increments -> end. Totals in accent, steps in grey.

    Direction is carried by position and a signed label, never by colour alone.
    """
    running = start
    xs, heights, bottoms, colours, texts, ticks = [], [], [], [], [], []

    xs.append(0); heights.append(start); bottoms.append(0)
    colours.append(accent); texts.append(money(start, unit, decimals))
    ticks.append(start_label)

    for i, (lab, d) in enumerate(zip(labels, deltas), start=1):
        bottom = running + d if d < 0 else running
        xs.append(i); heights.append(abs(d)); bottoms.append(bottom)
        colours.append(accent_down if d < 0 else MUTED)
        texts.append(money(d, unit, decimals, signed=True))
        ticks.append(lab)
        running += d

    xs.append(len(labels) + 1); heights.append(running); bottoms.append(0)
    colours.append(accent); texts.append(money(running, unit, decimals))
    ticks.append(end_label)

    ax.bar(xs, heights, bottom=bottoms, color=colours, width=0.6)

    # Connectors carry the running total across the gaps (Gestalt: continuity).
    level = start
    for i, d in enumerate(deltas, start=1):
        ax.plot([i - 1 + 0.3, i + 0.3], [level, level], color=MUTED, linewidth=0.8, zorder=0)
        level += d
    ax.plot([len(labels) + 0.3, len(labels) + 1 - 0.3], [level, level],
            color=MUTED, linewidth=0.8, zorder=0)

    ax.set_xticks(xs)
    ax.set_xticklabels(ticks, rotation=0)
    allv = [0, start, running] + [b + h for b, h in zip(bottoms, heights)]
    _enforce_zero(ax, axis="y", values=allv)

    span = max(allv) - min(allv) or 1.0
    for x, b, h, t, c in zip(xs, bottoms, heights, texts, colours):
        ax.text(x, b + h + span * 0.02, t, ha="center", va="bottom",
                color=INK if c == accent else GREY,
                fontweight="bold" if c == accent else "normal")
    declutter(ax, keep_x=True, keep_y=False)


# --- lines -------------------------------------------------------------------
def line(ax, x, series: dict, highlight=None, accent: str = ACCENT,
         unit: str = "", decimals: int = 1, label_end: bool = True) -> None:
    """Continuous data over consistent intervals, labelled at the line end.

    `series` maps name -> sequence of y values. Names are written at the right
    end of each line in the line's own colour (Gestalt: proximity + similarity),
    which removes the legend round-trip entirely.
    """
    highlight = set(highlight or ())
    for name, ys in series.items():
        signal = name in highlight or not highlight
        colour = accent if name in highlight else (BASE if highlight else accent)
        ax.plot(x, ys, color=colour, linewidth=2.4 if signal else 1.6,
                zorder=3 if signal else 2, solid_capstyle="round")
        if label_end:
            ax.text(x[-1], ys[-1], f"  {name}", va="center", ha="left",
                    color=colour, fontweight="bold" if name in highlight else "normal")
    if label_end:
        ax.margins(x=0.02)
        ax.set_xlim(min(x), max(x) + (max(x) - min(x)) * 0.14)
    declutter(ax, keep_x=True, keep_y=True)
    ax.tick_params(length=0)


def slopegraph(ax, left_label: str, right_label: str, series: dict,
               highlight=None, accent: str = ACCENT,
               unit: str = "", decimals: int = 0) -> None:
    """Two points in time; the slope shows rate of change without explaining it."""
    highlight = set(highlight or ())
    for name, (a, b) in series.items():
        colour = accent if name in highlight else MUTED
        weight = "bold" if name in highlight else "normal"
        lw = 2.4 if name in highlight else 1.2
        ax.plot([0, 1], [a, b], color=colour, linewidth=lw, zorder=3 if name in highlight else 2)
        ax.scatter([0, 1], [a, b], s=34 if name in highlight else 18,
                   color=colour, zorder=4)
        ax.text(-0.03, a, f"{name}  {money(a, unit, decimals)}", ha="right", va="center",
                color=colour if name in highlight else GREY, fontweight=weight)
        ax.text(1.03, b, f"{money(b, unit, decimals)}  {name}", ha="left", va="center",
                color=colour if name in highlight else GREY, fontweight=weight)

    ax.set_xlim(-0.45, 1.45)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([left_label, right_label])
    ax.xaxis.set_ticks_position("top")
    declutter(ax, keep_x=False, keep_y=False)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([left_label, right_label], fontweight="bold")
    ax.tick_params(length=0)


# --- table with visual cues --------------------------------------------------
def heatmap(ax, row_labels, col_labels, matrix, accent: str = ACCENT,
            fmt: str = "{:.0f}", legend_label: str = "LOW  ->  HIGH",
            cmap=None) -> None:
    """A table that keeps its detail but adds saturation as a visual cue.

    Saturation of ONE hue, never a rainbow: a rainbow destroys the preattentive
    value of colour and implies an ordering the hues do not carry.

    Signed data with a real zero wants two poles instead: pass
    `cmap=diverging_cmap()` and keep the printed values signed, so direction
    never rests on hue alone.
    """
    if cmap is None:
        cmap = (sequential_cmap() if accent == ACCENT
                else LinearSegmentedColormap.from_list("swd_seq", ["#ffffff", accent]))
    flat = [v for row in matrix for v in row]
    lo, hi = min(flat), max(flat)
    rng = (hi - lo) or 1.0

    ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=lo, vmax=hi)
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, rotation=0)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels)
    ax.xaxis.set_ticks_position("top")
    ax.tick_params(length=0)
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)

    for r, row in enumerate(matrix):
        for c, v in enumerate(row):
            # Keep text readable as the cell darkens.
            ax.text(c, r, fmt.format(v), ha="center", va="center",
                    color="white" if (v - lo) / rng > 0.55 else INK)
    ax.set_xlabel(legend_label, color=MUTED, labelpad=10)
    ax.xaxis.set_label_position("bottom")


# --- words -------------------------------------------------------------------
def annotate(ax, text: str, xy, xytext=None, accent: str = ACCENT,
             arrow: bool = True, bold: bool = False) -> None:
    """The words that carry the 'so what'. A chart without them is a picture."""
    kwargs = dict(color=accent if bold else GREY,
                  fontweight="bold" if bold else "normal",
                  ha="left", va="center", zorder=6)
    if xytext is None:
        ax.text(xy[0], xy[1], text, **kwargs)
        return
    ax.annotate(text, xy=xy, xytext=xytext, **kwargs,
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=1.0) if arrow else None)

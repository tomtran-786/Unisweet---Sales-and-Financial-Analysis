"""Chart linter: fails the checks that Storytelling with Data treats as rules.

Not a style opinion generator - each check corresponds to a specific failure
mode the book demonstrates with a broken chart:

  ZERO_BASELINE   truncated bar axis (the Fox News 35% -> 39.6% chart, which
                  renders a 13% increase as a 460% one)
  PIE / DONUT     asking the eye to compare angles and arc lengths
  THREE_D         3-D skews the values it plots
  SECOND_AXIS     two y-axes force the reader to decode which is which
  RAINBOW         >4 saturated hues destroys preattentive value
  NO_TITLE        an untitled chart makes the reader guess the takeaway
  TOPIC_TITLE     a descriptive title wastes the most valuable line on the page
  DIAGONAL_TICKS  45-degree text reads ~52% slower than horizontal
  LEGEND          a legend the reader must round-trip to; label directly
  CHARTJUNK       borders and dark gridlines competing with the data

Usage:
    python lint.py demo.py          # run a script, lint every figure it builds
    python lint.py out/*.py

    from lint import check
    problems = check(fig)           # -> list[Finding]
"""

from __future__ import annotations

import runpy
import sys
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Rectangle, Wedge

# Titles that describe the topic instead of stating the takeaway.
_TOPIC_WORDS = {"overview", "summary", "results", "analysis", "data", "report",
                "breakdown", "performance", "metrics", "kpis", "dashboard",
                "by month", "by category", "by region", "vs", "over time"}

SEVERITY_ORDER = {"error": 0, "warning": 1}


@dataclass
class Finding:
    code: str
    severity: str
    message: str
    where: str = ""

    def __str__(self) -> str:
        loc = f" [{self.where}]" if self.where else ""
        return f"{self.severity.upper():<7} {self.code:<14}{loc} {self.message}"


def _is_grey(colour, tol: float = 0.06) -> bool:
    try:
        r, g, b = to_rgb(colour)
    except (ValueError, TypeError):
        return True
    return max(r, g, b) - min(r, g, b) <= tol


def _bars(ax):
    """Rectangles that are data, not the axes background or a legend swatch."""
    out = []
    for p in ax.patches:
        if isinstance(p, Rectangle) and p.get_width() and p.get_height():
            if p is getattr(ax, "patch", None):
                continue
            out.append(p)
    return out


def _axes_label(fig, ax) -> str:
    try:
        return f"axes {fig.axes.index(ax) + 1}/{len(fig.axes)}"
    except ValueError:
        return "axes"


def check(fig) -> list[Finding]:
    """Lint one matplotlib Figure. Returns findings, most severe first."""
    out: list[Finding] = []

    titles = [t.get_text().strip() for t in fig.texts if t.get_text().strip()]
    titles += [ax.get_title().strip() for ax in fig.axes if ax.get_title().strip()]
    if not titles:
        out.append(Finding("NO_TITLE", "error",
                           "figure has no title; state the takeaway in words"))
    else:
        head = titles[0]
        low = head.lower()
        wordy = len(head.split())
        # A takeaway is a claim: it needs a verb and some length. A bare topic
        # phrase ("Q4 Performance Overview") is short and hits a topic word.
        if wordy <= 5 and any(w in low for w in _TOPIC_WORDS):
            out.append(Finding("TOPIC_TITLE", "warning",
                               f"title {head!r} names the topic; use an action title "
                               f"that states what the audience should conclude"))

    # twinx / twiny leave two axes stacked on the same rectangle.
    boxes: dict[tuple, int] = {}
    for ax in fig.axes:
        key = tuple(round(v, 4) for v in ax.get_position().bounds)
        boxes[key] = boxes.get(key, 0) + 1
    if any(n > 1 for n in boxes.values()):
        out.append(Finding("SECOND_AXIS", "error",
                           "two axes share one frame (twinx/twiny); label the second "
                           "series directly or split into stacked panels"))

    for ax in fig.axes:
        where = _axes_label(fig, ax)

        if ax.name == "3d" or type(ax).__name__ == "Axes3D":
            out.append(Finding("THREE_D", "error",
                               "3-D axes distort the values they plot", where))

        if any(isinstance(p, Wedge) for p in ax.patches):
            out.append(Finding("PIE", "error",
                               "pie/donut asks the eye to compare angles or arc "
                               "lengths; use a sorted horizontal bar chart", where))

        bars = _bars(ax)
        if bars:
            widths = {round(b.get_width(), 6) for b in bars}
            heights = {round(b.get_height(), 6) for b in bars}
            # Uniform width => vertical bars => y carries the magnitude.
            vertical = len(widths) <= len(heights)
            lo, hi = (ax.get_ylim() if vertical else ax.get_xlim())
            if not (min(lo, hi) <= 0 <= max(lo, hi)):
                axis = "y" if vertical else "x"
                out.append(Finding("ZERO_BASELINE", "error",
                                   f"bar chart {axis}-limits {(round(lo, 3), round(hi, 3))} "
                                   f"exclude zero; bar length must be read from zero",
                                   where))

        hues = {tuple(round(c, 3) for c in to_rgb(b.get_facecolor()))
                for b in bars if not _is_grey(b.get_facecolor())}
        hues |= {tuple(round(c, 3) for c in to_rgb(ln.get_color()))
                 for ln in ax.get_lines() if not _is_grey(ln.get_color())}
        if len(hues) > 4:
            out.append(Finding("RAINBOW", "warning",
                               f"{len(hues)} saturated colours; short-term memory holds "
                               f"about four - grey the context, accent the signal", where))

        if ax.get_legend() is not None:
            out.append(Finding("LEGEND", "warning",
                               "legend forces a round-trip between key and data; "
                               "label the series at its end point instead", where))

        for lab in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
            rot = lab.get_rotation() % 180
            if 0 < rot < 90 or 90 < rot < 180:
                out.append(Finding("DIAGONAL_TICKS", "warning",
                                   f"tick labels rotated {lab.get_rotation():.0f} degrees; "
                                   f"abbreviate them and keep text horizontal", where))
                break

        junk = [s for s in ("top", "right") if ax.spines[s].get_visible()]
        if junk:
            out.append(Finding("CHARTJUNK", "warning",
                               f"{'/'.join(junk)} spine(s) visible; the chart reads as "
                               f"complete without a border", where))

        gridlines = [g for g in (ax.get_xgridlines() + ax.get_ygridlines())
                     if g.get_visible() and g.get_alpha() not in (0,)]
        if gridlines and ax.xaxis._major_tick_kw.get("gridOn", False):
            dark = [g for g in gridlines if not _is_grey(g.get_color())
                    or sum(to_rgb(g.get_color())) < 1.8]
            if dark:
                out.append(Finding("CHARTJUNK", "warning",
                                   "gridlines are dark enough to compete with the data; "
                                   "drop them or push them to light grey", where))

    out.sort(key=lambda f: SEVERITY_ORDER[f.severity])
    return out


def check_all() -> list[tuple[int, Finding]]:
    """Lint every figure currently open."""
    results = []
    for num in plt.get_fignums():
        for f in check(plt.figure(num)):
            results.append((num, f))
    return results


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2

    total_err = 0
    for script in argv:
        plt.close("all")
        runpy.run_path(script, run_name="__lint__")
        results = check_all()
        errs = [f for _, f in results if f.severity == "error"]
        total_err += len(errs)
        print(f"\n{script}: {len(plt.get_fignums())} figure(s), "
              f"{len(errs)} error(s), {len(results) - len(errs)} warning(s)")
        for num, f in results:
            print(f"  fig {num}: {f}")
        if not results:
            print("  clean")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

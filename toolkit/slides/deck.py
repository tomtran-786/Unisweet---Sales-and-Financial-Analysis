"""Slide-design driver: one spec, two renderings.

The slideument problem is that a live deck and a circulated deck want different
densities, and one artifact aimed at the middle serves neither. The answer here
is not to choose a density but to write the content once and render it twice:

    build_pptx(slides, path)   sparse - title + visual, everything else in notes
    build_pdf(slides, path)    annotated - takeaway on the page, narration under it

Both consume the same list of `Slide`, so the two files cannot drift apart.

Geometry is deliberately identical to the chart canvas. `visualisations.ipynb`
exports headerless twins to outputs/report_visuals/slides/ by hiding its
figure-level header and source line while leaving the axes untouched, so those
PNGs carry empty bands exactly where this module puts native text back. Nothing
is scaled or cropped; the charts keep the alignment they were tuned for.

Palette comes from the sibling storytelling-with-data skill. It is imported, not
copied, so the deck and the charts have one definition of the visual system.
"""

from __future__ import annotations

import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
# The chart toolkit is a sibling directory, but it is named differently depending on
# where this file lives: `charts` inside the repository, `storytelling-with-data`
# when the two are installed side by side as skills. Try both rather than pinning
# one layout and breaking the other.
for _candidate in (HERE.parent / "charts", HERE.parent / "storytelling-with-data"):
    if (_candidate / "swd.py").exists():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break
else:  # pragma: no cover - a layout we have not seen
    raise ImportError(
        f"deck.py needs swd.py from the chart toolkit; looked for a sibling "
        f"'charts' or 'storytelling-with-data' directory next to {HERE}"
    )

import swd  # noqa: E402  - the one definition of the palette

__all__ = ["Slide", "build_pptx", "build_pdf", "W_IN", "H_IN"]

# --- geometry ----------------------------------------------------------------
# 16:9 at the charts' own export size. Fractions match add_header/add_footer.
W_IN, H_IN = 40 / 3, 7.5
LEFT = 0.055                      # the one left edge, for every rendering
RIGHT = 0.945
EYEBROW_Y = 0.980                 # the signpost: where the reader is
TITLE_Y = 0.940                   # top of the title block
SUB_Y = 0.886
TAKEAWAY_Y = 0.836                # circulated rendering only
NARRATION_Y = 0.088               # circulated rendering only
SOURCE_Y = 0.030

# In the circulated rendering the chart is cropped to its ink and placed in the
# band between the header and the narration, so the narration gets real space
# instead of landing on top of the axis labels.
ART_TOP = 0.79
ART_BOTTOM = 0.17

TITLE_PT = 23.0
SUB_PT = 11.5
TAKEAWAY_PT = 13.0
NARRATION_PT = 9.5
SOURCE_PT = 8.5
FONT = "Arial"

# --- palette, inherited ------------------------------------------------------
INK = swd.INK
MID = swd.GREY
MUTED = swd.MUTED
ACCENT = swd.ACCENT
CONTRA = swd.ACCENT_2
PALE = swd.SEQ_BLUE[-1]

# Narration has to fit the band the chart leaves free at the bottom. Keeping it
# tight is also the right editorial discipline - crisp beats complete.
NARRATION_WRAP = 118
NARRATION_MAX_LINES = 3


def fit_title(title: str) -> float:
    """Titles are edited to fit; rendering never shrinks the argument."""
    return TITLE_PT


def ink_bbox(png: Path, pad: int = 8) -> tuple[int, int, int, int]:
    """Crop box around everything that is not page white.

    The chart twins keep the full 16:9 canvas with empty header and footer
    bands. Full bleed is right for the .pptx, where native text fills those
    bands. The circulated page needs the bands back as narration space, so it
    crops to the ink instead of guessing fixed margins per chart.
    """
    import numpy as np
    from PIL import Image

    with Image.open(png) as im:
        arr = np.asarray(im.convert("L"))
    rows = np.where((arr < 250).any(axis=1))[0]
    cols = np.where((arr < 250).any(axis=0))[0]
    if not len(rows) or not len(cols):
        return (0, 0, arr.shape[1], arr.shape[0])
    return (max(int(cols[0]) - pad, 0), max(int(rows[0]) - pad, 0),
            min(int(cols[-1]) + pad, arr.shape[1]), min(int(rows[-1]) + pad, arr.shape[0]))


def wrap_narration(text: str) -> list[str]:
    lines = textwrap.wrap(text, NARRATION_WRAP) if text else []
    if len(lines) > NARRATION_MAX_LINES:
        raise ValueError(
            f"narration needs {len(lines)} lines, band fits {NARRATION_MAX_LINES}: {text[:70]}..."
        )
    return lines


@dataclass
class Slide:
    """One unit of the argument, in whichever rendering."""

    kind: str = "chart"          # title | statement | summary | section | chart | actions | closing
    title: str = ""              # the action title - the claim, never the topic
    subtitle: str = ""
    takeaway: str = ""           # the "so what", on the page when circulated
    narration: str = ""          # what the presenter would say
    image: Path | None = None    # headerless chart twin
    source: str = ""
    bullets: list = field(default_factory=list)   # str, or (label, body) pairs
    eyebrow: str = ""            # signpost: where the reader is

    def notes(self) -> str:
        parts = [p for p in (self.takeaway, self.narration) if p]
        if self.source:
            parts.append(f"[Sources]\n- {self.source}")
        return "\n\n".join(parts)


# --- rendering 1: the room ---------------------------------------------------
def build_pptx(slides: list[Slide], path: Path) -> Path:
    """Sparse slides. Takeaway and narration live in the speaker notes."""
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.util import Inches, Pt

    def rgb(hexstr: str) -> RGBColor:
        return RGBColor.from_string(hexstr.lstrip("#").upper())

    def textbox(slide, x, y, w, h, text, size, colour, bold=False, spacing=1.15):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        for i, chunk in enumerate(text.split("\n")):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.line_spacing = spacing
            run = para.add_run()          # never tf.text - it drops the styling
            run.text = chunk
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.name = FONT
            run.font.color.rgb = rgb(colour)
        return box

    prs = Presentation()
    prs.slide_width = Inches(W_IN)
    prs.slide_height = Inches(H_IN)
    blank = prs.slide_layouts[6]

    for spec in slides:
        slide = prs.slides.add_slide(blank)

        if spec.image:
            # Full bleed. The empty bands in the twin are where the text goes.
            slide.shapes.add_picture(str(spec.image), 0, 0,
                                     width=Inches(W_IN), height=Inches(H_IN))

        x = LEFT * W_IN
        width = (RIGHT - LEFT) * W_IN

        if spec.eyebrow:
            textbox(slide, x, (1 - EYEBROW_Y) * H_IN, width, 0.25,
                    spec.eyebrow.upper(), 9.5, MUTED, bold=True)

        if spec.kind == "title":
            textbox(slide, x, H_IN * 0.34, width, 1.6, spec.title, 40, ACCENT, bold=True)
            if spec.subtitle:
                textbox(slide, x, H_IN * 0.56, width, 1.0, spec.subtitle, 15, MID)
        elif spec.title:
            textbox(slide, x, (1 - TITLE_Y) * H_IN, width, 0.9,
                    spec.title, fit_title(spec.title), ACCENT, bold=True)
            if spec.subtitle:
                textbox(slide, x, (1 - SUB_Y) * H_IN, width, 0.6, spec.subtitle, SUB_PT, MID)

        if spec.bullets:
            _pptx_bullets(spec, slide, textbox, x, width)

        if spec.source:
            textbox(slide, x, H_IN - (SOURCE_Y * H_IN) - 0.20, width, 0.20,
                    f"Source: {spec.source}", SOURCE_PT, MUTED)

        # Read notes_slide before writing or python-pptx never creates the part.
        slide.notes_slide.notes_text_frame.text = spec.notes()

    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(path))
    return path


def _pptx_bullets(spec, slide, textbox, x, width):
    """Statement, summary, actions and closing bodies."""
    top = H_IN * (0.26 if spec.kind == "statement" else 0.24)
    if spec.kind == "statement":
        textbox(slide, x, top, width, 2.4, spec.bullets[0], 26, INK, bold=True, spacing=1.30)
        y = top + 2.6
        for line in spec.bullets[1:]:
            if not line:
                y += 0.20
                continue
            textbox(slide, x, y, width, 0.80, line, 13, MID, spacing=1.45)
            y += 0.55 if len(line) > 110 else 0.36
        return

    if spec.kind == "actions":
        col_w = (width - 0.7) / 3
        for i, (head, body) in enumerate(spec.bullets):
            cx = x + i * (col_w + 0.35)
            textbox(slide, cx, top, col_w, 0.9, head, 15, ACCENT, bold=True, spacing=1.20)
            textbox(slide, cx, top + 1.0, col_w, 3.0, body, 12, INK, spacing=1.40)
        return

    for i, item in enumerate(spec.bullets):
        y = top + i * 0.92
        if isinstance(item, (tuple, list)):
            label, body = item
            textbox(slide, x, y, width, 0.28, label, 12, ACCENT if spec.kind == "closing" else MID, bold=True)
            textbox(slide, x, y + 0.28, width, 0.52, body, 14, INK, spacing=1.25)
        else:
            textbox(slide, x, y, width, 0.5, item, 15, INK, spacing=1.30)


# --- rendering 2: the reader -------------------------------------------------
def build_pdf(slides: list[Slide], path: Path) -> Path:
    """Same title and visual, plus the takeaway and narration on the page."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [FONT, "Helvetica", "DejaVu Sans"],
        "pdf.fonttype": 42,          # embed as TrueType so the text stays selectable
    })

    path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(str(path)) as pdf:
        for spec in slides:
            fig = plt.figure(figsize=(W_IN, H_IN), dpi=144)
            fig.patch.set_facecolor("white")

            if spec.image:
                _place_art(fig, spec.image)

            if spec.eyebrow:
                fig.text(LEFT, EYEBROW_Y, spec.eyebrow.upper(), ha="left", va="top",
                         fontsize=9.5, color=MUTED, fontweight="bold")

            if spec.kind == "title":
                fig.text(LEFT, 0.62, spec.title, ha="left", va="top",
                         fontsize=40, color=ACCENT, fontweight="bold")
                if spec.subtitle:
                    fig.text(LEFT, 0.44, spec.subtitle, ha="left", va="top",
                             fontsize=15, color=MID, linespacing=1.5)
            elif spec.title:
                fig.text(LEFT, TITLE_Y, spec.title, ha="left", va="top",
                         fontsize=fit_title(spec.title), color=ACCENT, fontweight="bold")
                if spec.subtitle:
                    fig.text(LEFT, SUB_Y, spec.subtitle, ha="left", va="top",
                             fontsize=SUB_PT, color=MID)

            # The annotation layer - this is what replaces the presenter.
            if spec.takeaway:
                fig.text(LEFT, TAKEAWAY_Y, spec.takeaway, ha="left", va="top",
                         fontsize=TAKEAWAY_PT, color=INK,
                         fontweight="bold", linespacing=1.35)

            if spec.bullets:
                _pdf_bullets(spec, fig)

            lines = wrap_narration(spec.narration)
            if lines:
                fig.text(LEFT, NARRATION_Y + 0.028 * (len(lines) - 1), "\n".join(lines),
                         ha="left", va="bottom", fontsize=NARRATION_PT,
                         color=MID, linespacing=1.45)

            if spec.source:
                fig.text(LEFT, SOURCE_Y, f"Source: {spec.source}", ha="left", va="bottom",
                         fontsize=SOURCE_PT, color=MUTED)

            pdf.savefig(fig, facecolor="white")
            plt.close(fig)
    return path


def _place_art(fig, image: Path) -> None:
    """Crop the chart to its ink and centre it in the band left for artwork.

    Aspect is preserved, so a wide chart keeps its width and a tall one keeps
    its height; whichever dimension binds decides the other.
    """
    import matplotlib.image as mpimg

    x0, y0, x1, y1 = ink_bbox(image)
    art = mpimg.imread(str(image))[y0:y1, x0:x1]

    box_w, box_h = RIGHT - LEFT, ART_TOP - ART_BOTTOM
    page_aspect = W_IN / H_IN
    art_aspect = (art.shape[1] / art.shape[0]) / page_aspect   # in figure-fraction terms

    if art_aspect >= box_w / box_h:      # width-bound
        w, h = box_w, box_w / art_aspect
    else:                                 # height-bound
        w, h = box_h * art_aspect, box_h

    left = LEFT + (box_w - w) / 2
    bottom = ART_BOTTOM + (box_h - h) / 2
    ax = fig.add_axes([left, bottom, w, h])
    ax.imshow(art, interpolation="antialiased")
    ax.axis("off")


def _pdf_bullets(spec, fig) -> None:
    top = 0.74 if spec.kind == "statement" else 0.76

    if spec.kind == "statement":
        fig.text(LEFT, top, spec.bullets[0], ha="left", va="top",
                 fontsize=26, color=INK, fontweight="bold", linespacing=1.45)
        y = 0.46
        for line in spec.bullets[1:]:
            # Nothing may run past the right margin; long lines wrap, they do
            # not get clipped.
            wrapped = textwrap.fill(line, 132) if line else ""
            fig.text(LEFT, y, wrapped, ha="left", va="top",
                     fontsize=13, color=MID, linespacing=1.55)
            y -= 0.055 * (wrapped.count("\n") + 1) + 0.020
        return

    if spec.kind == "actions":
        for i, (head, body) in enumerate(spec.bullets):
            x = LEFT + i * 0.302
            fig.text(x, top, head, ha="left", va="top",
                     fontsize=15, color=ACCENT, fontweight="bold", linespacing=1.30)
            fig.text(x, top - 0.13, body, ha="left", va="top",
                     fontsize=12, color=INK, linespacing=1.55)
        return

    # Bodies wrap to the right margin rather than running off the page.
    BODY_WRAP = 116
    wrapped = [
        (item[0], textwrap.fill(item[1], BODY_WRAP)) if isinstance(item, (tuple, list))
        else textwrap.fill(item, BODY_WRAP)
        for item in spec.bullets
    ]
    rows = sum((w[1] if isinstance(w, tuple) else w).count("\n") + 1 for w in wrapped)
    step = (top - 0.20) / max(rows + len(wrapped) * 0.6, 1)

    y = top
    for item in wrapped:
        if isinstance(item, tuple):
            label, body = item
            fig.text(LEFT, y, label, ha="left", va="top", fontsize=12,
                     color=ACCENT if spec.kind == "closing" else MID, fontweight="bold")
            fig.text(LEFT, y - 0.038, body, ha="left", va="top", fontsize=14,
                     color=INK, linespacing=1.35)
            y -= step * (body.count("\n") + 1.6)
        else:
            fig.text(LEFT, y, item, ha="left", va="top", fontsize=15,
                     color=INK, linespacing=1.40)
            y -= step * (item.count("\n") + 1.6)

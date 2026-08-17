---
name: slide-design
description: Build executive slide decks that work both presented live and circulated to people who were not in the room - action-title-first structure, Pyramid Principle ordering, callout-box annotation instead of animation, speaker notes, and a one-spec/two-rendering pptx + PDF builder. Use when asked to build, structure, review or fix a slide deck, presentation, board or exec readout, pre-read or leave-behind, or to turn charts and a storyline into slides.
---

# Slide design

How to build a deck that survives being sent on without you. Distilled from two
sources, both converted in full into `reference/`:

- Cole Nussbaumer Knaflic, *Storytelling with Data* (Wiley, 2015), Part 3 — the
  case studies, including the slideument problem at p.211 and the
  compress-the-progression answer at p.226.
- Hern Lee, *From Blah to Boardroom: The Science Behind Exec-Ready
  Presentations* — 4 pillars (Setup, Headlines, Content, Visuals), 24 principles.

**Paths below are relative to the repo root.**

| File | What it is |
|---|---|
| `toolkit/slides/deck.py` | The driver. One slide spec, rendered to a sparse `.pptx` and an annotated `.pdf`. |
| `toolkit/slides/reference/slideument.md` | The distilled doctrine — read this before structuring a deck. |
| `toolkit/slides/reference/from-blah-to-boardroom.md` | Full conversion, for looking up a principle in context. |
| `toolkit/slides/reference/storytelling-with-data-p3.md` | Full conversion, same purpose. |

Charts come from the sibling `storytelling-with-data` skill. Palette, gridline,
greying and Z-alignment rules live there and are imported, never restated — see
`toolkit/charts/SKILL.md`. `deck.py` imports `swd` for
colour so there is exactly one definition of the visual system.

## The one rule this skill exists for

**Assume the deck will be read without you.** Not because that is the plan, but
because plans break: execs interrupt, arrive late, cut the agenda, or cancel and
ask you to send it over. A deck that only works with a presenter attached fails
silently the moment it is forwarded.

That does not mean dumping text on every slide. It means every slide carries a
self-enclosed claim, and the reasoning lives somewhere the reader can reach.

## One spec, two renderings

Knaflic's continuum runs from live presentation (you control pace, slides stay
sparse) to written document (the reader controls pace, so detail must be on the
page). A single artifact aimed at the midpoint is the *slideument* — too dense to
project, too thin to read alone.

The resolution is not to pick a point on the continuum. It is to write the
content once and render it twice:

| Rendering | Audience | Carries |
|---|---|---|
| `.pptx` | the room | Action title + chart. Takeaway and narration go in **speaker notes**. |
| `.pdf` | absentees | Same title and chart, plus the takeaway **on the page** and the narration beneath it. |

Both come from the same `Slide` list, so they cannot drift. `deck.py` enforces
this: it takes one spec and writes both files.

## Structure

**Pyramid Principle, always** (Minto, via Boardroom). Lead with the answer, then
the supporting arguments, then the data underneath. You think bottom-up; you
present top-down. A deck that walks through method before conclusion is a
research log, not a readout.

**Write the headlines first**, then pressure-test them with two questions:

1. Delete everything except the headlines. Do they still tell a coherent story?
2. Does each slide's content actually support its own headline?

A "no" anywhere is work to do, not a slide to polish.

**Headline quality: strong, direct, crisp.** Strong means action-led or
assertive, never passive and never a claim nobody would contest. Direct means
plain words; corporate register makes readers either decode or tune out. Crisp
means short *and* pointed — "our DAUs have trended down for three quarters" is
short; "we're losing users" is crisp.

**Commentate, don't just label.** "FY2024 sales by market" labels. "Every market
beat plan" commentates. Anywhere you get a header or a caption, spend it on the
insight; keep the labelling on the chart itself where it belongs.

**Be deliberate about order** — importance, urgency or impact, not the order you
happened to do the work in.

**Signpost.** In anything with sections, tell the reader where they are. Not
knowing whether you are 10% or 70% through is a distraction that costs attention.

**Use the appendix and the pre-read.** You do not have to cover everything live.
Detail that establishes credibility but would burn discussion time belongs in the
appendix; context the audience needs beforehand belongs in a pre-read.

**Every slide sells something** — an ask, a decision, a reframe. A slide that
sells nothing is a slide to cut.

## Annotation, not animation

The two sources disagree here, and the disagreement is worth knowing.

Knaflic builds a live progression by revealing one component at a time, then
**compresses the whole progression into a single annotated visual** for
circulation. Boardroom rejects the live half outright: with executives you do not
control the flow, they interject, and being mid-animation when a question lands
leaves you clicking around for the right slide. Its exception is narrow — a
townhall or anything where you present unilaterally.

**Resolve it toward the compressed version.** Build the one annotated visual with
callout boxes and direct labels, and keep it on a single slide. That is both
Knaflic's circulated artifact and Boardroom's foolproof live slide, and it is the
form that still works when the deck is forwarded. Pseudo-animation — the same
chart duplicated across slides with a different section highlighted each time —
is the fallback for a talk you fully control, not the default.

This is why the charts in this repo carry their own callouts and caveats: each
one is already the compressed annotated visual, so the deck does not have to
rebuild it.

## Run

```bash
python3 scripts/build_deck.py
```

Writes `outputs/deck/*.pptx` and `outputs/deck/*.pdf` from the `SLIDES` spec in
that script. `deck.py` is the library it calls.

Then **open both and read them.** Specifically: read only the slide titles, top
to bottom, and check they alone carry the argument; then read two pages of the
PDF cold, as someone who missed the meeting would.

## Gotchas

- **Charts need a headerless twin.** A chart that bakes in its own title will
  double up against the slide's native title. `visualisations.ipynb` exports
  these to `outputs/report_visuals/slides/` by hiding figure-level chrome and
  keeping the axes geometry identical, so the empty top and bottom bands are
  exactly where the native title and source line go.
- **Reuse action titles from the manifest**, never retype them.
  `outputs/report_visuals/visual_manifest.csv` has the verified column; typing
  them again lets the deck and the charts drift apart.
- **python-pptx has no notes placeholder until you touch it** — read
  `slide.notes_slide` before writing, or the notes silently vanish.
- **Speaker notes are not a safety net for the circulated version.** Most people
  who open a forwarded `.pptx` never look at the notes pane. That is what the PDF
  rendering is for.

# Planning worksheet

The parts of the method that are decisions, not code. Distilled from
`references/domain/storytelling-with-data-p1.md` (Knaflic, *Storytelling with
Data*, Wiley 2015), chapters 1, 3, 4 and 7.

## 1. Context, before any chart exists

Exploratory analysis opens a hundred oysters. Explanatory communication shows
the two pearls. Everything below is about the second.

**Who** — one named audience, ideally the decision maker. "Internal and
external stakeholders" is not an audience; a communication aimed at everyone
lands with no one. Note what they already believe and what would make them
resist.

**What** — the action, as a verb: approve, fund, stop, reprioritise,
investigate. If you cannot state it, reconsider whether to communicate at all.
Presenting data without an ask invites "interesting" and nothing else.

**How** — only now, the data. It is evidence for the ask, not a substitute
for it. Show the data that cuts against you too; a discerning audience will
find it, and finding it themselves costs you the argument.

**Mechanism** — live presentation (you control pace, slides stay sparse) or
written document (reader controls pace, detail must be on the page). Decide
which before you set density. A deck that tries to be both serves neither.

**Tone** — celebratory, urgent, clinical. It drives the palette.

### The Big Idea
One sentence that (a) states your point of view, (b) conveys what is at stake,
(c) is a complete sentence. If you can't write it, you don't have the story yet.

### The 3-minute story
What you would say with no slides at all, in three minutes. This is what
survives when your half-hour becomes five minutes.

### Storyboard
Outline before you open any software. Use paper or sticky notes — work created
on screen acquires a sunk-cost attachment that makes it hard to cut.

## 2. Structure

Three acts: setup, conflict, resolution. The tension between "what is" and
"what could be" is what holds attention; a story where everything is fine is
not a story.

- **Beginning** — setting, the imbalance, why it matters to *them*.
- **Middle** — evidence, what happens if nothing changes, options, why yours.
- **End** — the call to action, tied back to the opening tension.

**Order.** Chronological (problem → analysis → finding → ask) builds
credibility with a new audience. Lead-with-the-ending suits an audience that
trusts you and wants the "so what". Say which you are doing.

**Repetition.** Executive summary → detail → recap. Redundant to you, helpful
to them, and it is what makes the message stick.

## 3. Decluttering pass

Every element spends the audience's cognitive budget. Remove anything that
isn't earning its place:

1. Chart border — the eye completes the shape without it (closure).
2. Gridlines — remove. `swd.use()` sets `axes.grid: False` and charts in this
   repo carry none. Once every mark is labelled directly the value axis goes
   too; keep only the zero line, which is a reference, not a grid.
3. Data markers on every point — use them as "look here" signals, sparingly.
4. Trailing zeros on axis labels — they add length, not meaning.
5. Legends — label the series directly, next to the data (proximity).
6. Label colour — match it to the data it names (similarity).
7. Diagonal text — 45° reads about 52% slower. Abbreviate and stay horizontal.

Keep `$`, `%` and thousands separators on the numbers themselves. That
redundancy is not clutter; it removes a lookup.

Then check **alignment** and **white space** (preserve margins; never add data
to fill a gap).

Alignment means one left edge for every word on the page. The eye reads a page
as a Z — in at the top-left, right across the title, diagonally down through
the plot, then right again along the source line — and each of those sweeps
should start from the same place. Centred text creates no edge to start from,
so the eye has to re-find the beginning of every line.

The exception is a label attached to a mark: bar-end values, waterfall step
labels, heatmap cell values, line end-labels. Proximity is what tells the
reader which number belongs to which shape, so those stay on their mark.
Left-align the words; leave the numbers where the data is.

## 4. Attention

Grey is the base, one colour is the signal. Contrast only works when it is
scarce — a hawk is easy to spot among pigeons, hard among many kinds of bird.

Short-term memory holds about four chunks, so keep saturated colours to four
or fewer. Some preattentive attributes carry quantity (length, position, and
weakly size/width/intensity); hue does not — use it to categorise, never to
rank. Saturation of a single hue can rank; a rainbow cannot.

Two ramps exist for the cases one accent cannot cover — `SEQ_BLUE`
(`#004c6d #346888 #5886a5 #7aa6c2 #9dc6e0 #c1e7ff`) and `SEQ_ORANGE`
(`#f79545 #faa35e #fdb177 #ffbf8f #ffcda8 #ffdbc1`). **Blue marks favourable
movement, orange marks adverse.** Favourable means good for the business, not
positive in sign: a cut in cost is blue even though it prints with a minus.
Read the meaning, not the sign — and remember the adverse pole flips with the
metric, so falling turnover and *rising* discount rate are both orange.

Orange is a fill colour, not a text colour: its darkest step reaches only
2.3:1 against white. Label anything orange in `INK`.

Never encode direction in colour alone: red/green fails for ~8% of men. Add a
sign, a position, or a mark.

Highlight at most ~10% of the visual. Highlighting everything highlights nothing.

**The test:** look away, look back, and note where your eye lands first. If it
isn't the thing you want seen, the design is wrong. Better still, ask someone
without context to narrate what they notice, in order.

## 5. Final checks

- **Horizontal logic** — read only the titles, top to bottom. Together they
  should be the argument. This requires action titles.
- **Vertical logic** — on each page, title, visual and words reinforce each
  other, with nothing extraneous.
- **Reverse storyboarding** — write down each page's main point from the
  finished deck. That list should match the storyboard you started with.
- **Fresh perspective** — hand it to someone with no context and ask what they
  pay attention to, what they conclude, and what they'd ask. You are too close
  to your own work to see it as they will.

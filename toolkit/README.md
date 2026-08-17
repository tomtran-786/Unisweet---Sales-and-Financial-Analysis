# toolkit

Two small Python libraries that hold the visual method used throughout this project, so it
is executable rather than a style guide nobody rereads.

| Directory | What it is |
|---|---|
| [`charts/`](charts/) | `swd.py` builds the chart forms; `lint.py` fails a figure that breaks the rules; `demo.py` renders one worked example of every form into `gallery/`. |
| [`slides/`](slides/) | `deck.py` renders one slide specification two ways — a sparse `.pptx` for presenting and an annotated `.pdf` for circulating. |

`visualisations.ipynb` imports `charts/`; `scripts/build_deck.py` imports `slides/`.
Neither has any dependency outside `requirements.txt`.

## How these were built

Each library began as a book, read and then compressed into something a machine can check:

1. **Convert.** The source books were converted from PDF to Markdown with `fastpdf4llm`,
   figures extracted alongside the text.
2. **Distil.** The parts that are *decisions* rather than code were written up in original
   words, with attribution and page references — [`charts/reference/planning.md`](charts/reference/planning.md)
   (audience, action, chart choice) and [`slides/reference/slideument.md`](slides/reference/slideument.md)
   (the live-versus-circulated problem).
3. **Encode.** The parts that are *mechanical* became code. Grey-plus-one-accent, direct
   labels, no gridlines, zero-based bars: each is a function in `swd.py` or a check in
   `lint.py`, so a chart that breaks one fails at export instead of at review.
4. **Write the entry point.** Each `SKILL.md` is the operating manual — when to reach for
   which form, the palette and its contrast limits, and the mistakes that cost real
   debugging time on this project.

Sources: Cole Nussbaumer Knaflic, *Storytelling with Data* (Wiley, 2015), and Hern Lee,
*From Blah to Boardroom*.

> **The full book conversions are not in this repository.** Each `reference/` folder here
> holds only the original distillations written for this project. The converted book text
> and the extracted figures stay local and are gitignored, for copyright reasons.

## Using them elsewhere

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

Then open the PNG and look at it. The linter checks structure, not whether two labels
overlap.

Rebuild the gallery, and confirm the linter still bites (it must report 4 errors and
10 warnings against the deliberately bad examples):

```bash
cd toolkit/charts && python3 demo.py && python3 lint.py bad_examples.py
```

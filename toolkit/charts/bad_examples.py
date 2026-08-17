"""Charts that break the rules on purpose - the linter's test fixture.

`python lint.py bad_examples.py` must flag every one of these. If a check ever
stops firing here, the check is broken, not the chart.

Nothing in this file is a pattern to copy. See demo.py for that.
"""

import matplotlib.pyplot as plt
import numpy as np

# 1. Truncated bar axis - the Fox News chart: a 13% rise drawn as a 460% one.
fig1, ax1 = plt.subplots()
ax1.bar(["Now", "Jan 1"], [35, 39.6], color="#e8a33d")
ax1.set_ylim(34, 42)
fig1.suptitle("If Bush tax cuts expire")

# 2. Pie chart - eye cannot rank the wedges.
fig2, ax2 = plt.subplots()
ax2.pie([34, 31, 26, 9], labels=["A", "B", "C", "D"])
fig2.suptitle("Supplier Market Share")

# 3. Rainbow series + legend + diagonal ticks + chartjunk, all at once.
fig3, ax3 = plt.subplots()
x = np.arange(6)
for name, colour in [("North", "#d62728"), ("South", "#2ca02c"), ("East", "#ff7f0e"),
                     ("West", "#9467bd"), ("Central", "#17becf"), ("Online", "#e377c2")]:
    ax3.plot(x, np.random.default_rng(abs(hash(name)) % 2**32).integers(1, 9, 6),
             label=name, color=colour)
ax3.legend()
ax3.grid(True, color="#333333")
ax3.spines["top"].set_visible(True)
ax3.spines["right"].set_visible(True)
ax3.set_xticks(x)
ax3.set_xticklabels(["January", "February", "March", "April", "May", "June"], rotation=45)
ax3.set_title("Regional Performance Overview")

# 4. Secondary y-axis - reader must decode which series belongs to which scale.
fig4, ax4 = plt.subplots()
ax4.bar(range(8), [0.6, 0.5, 0.9, 1.0, 0.8, 0.9, 1.0, 1.0])
ax4b = ax4.twinx()
ax4b.plot(range(8), [91, 105, 112, 111, 109, 110, 110, 112], color="#ff7f0e")
ax4.set_title("Revenue and Headcount")

# 5. 3-D bars - bar height is read off an invisible tangent plane.
fig5 = plt.figure()
ax5 = fig5.add_subplot(projection="3d")
ax5.bar3d([0, 1, 2], [0, 0, 0], [0, 0, 0], 0.5, 0.5, [1, 1, 3])
ax5.set_title("Number of issues")

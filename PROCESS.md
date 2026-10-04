I chose Hong Kong rainfall after discussing a few ideas with Codex.


I kept the circular layout because I wanted something more distinctive. I
rejected the calendar heatmap because it felt too ordinary.


I used Codex to draft `plot.py`. The first version read the saved CSV and used
Matplotlib to draw the chart, with small dots for trace rainfall.

I found the small rainfall hard to see. I rejected thicker lines and asked for
longer lines that bend at the edge. Codex first understood this as arc-only
lines. I clarified that I wanted straight lines with curved ends. It implemented
the change with total length proportional to rainfall.


I then asked for less text and a bigger circle. Codex reduced the labels and
expanded the straight sections, leaving only eight days with curved ends.

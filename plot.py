# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""Draw the first rainfall fingerprint from the saved CSV: uv run plot.py."""

import calendar
import csv
import math
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "data" / "daily_HKO_RF_ALL.csv"
OUTPUT = HERE / "out" / "rainfall-fingerprint-2025.png"
YEAR = 2025
PAPER = "#FAF8F4"
INK = "#183F4D"
RAIN = "#2A7886"
TRACE = "#8A9FA4"
GRID = "#D8D9D2"


def load_year(path: Path = SOURCE, year: int = YEAR) -> list[tuple[date, float | None]]:
    """Read every day in the selected year; None means trace, not missing data."""
    records = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)  # Chinese title.
        next(reader, None)  # English title.
        header = next(reader, None)
        if not header or len(header) != 5 or not header[0].endswith("/Year"):
            raise ValueError("The saved CSV does not have the expected HKO header.")

        for line_number, row in enumerate(reader, start=4):
            if not row or row[0] != str(year):
                continue  # Other years and the publisher's footer notes.
            if len(row) != 5:
                raise ValueError(f"CSV line {line_number}: expected five fields.")

            row_year, month, day, value, complete = row
            when = date(int(row_year), int(month), int(day))
            if when in records:
                raise ValueError(f"Duplicate date: {when}.")
            if complete != "C":
                raise ValueError(f"{when}: the rainfall record is incomplete.")

            rainfall = None if value == "Trace" else float(value)
            if rainfall is not None and (not math.isfinite(rainfall) or rainfall < 0):
                raise ValueError(f"{when}: invalid rainfall value {value!r}.")
            records[when] = rainfall

    expected_days = (date(year + 1, 1, 1) - date(year, 1, 1)).days
    if len(records) != expected_days:
        raise ValueError(f"Expected {expected_days} dates in {year}, found {len(records)}.")
    return sorted(records.items())


def draw_fingerprint(records: list[tuple[date, float | None]]) -> None:
    """Give each day an equal angle, and use its rainfall as the bar height."""
    year = records[0][0].year
    day_angle = math.tau / len(records)
    inner_radius = 160  # A layout offset for the empty centre, not rainfall.
    angles, amounts, trace_angles = [], [], []

    for index, (when, rainfall) in enumerate(records):
        angle = index * day_angle
        if rainfall is None:
            trace_angles.append(angle)
        else:
            angles.append(angle)
            amounts.append(rainfall)

    # Round the scale upward without cutting off any unusually wet day.
    scale_max = max(400, math.ceil(max(amounts) / 100) * 100)
    figure = plt.figure(figsize=(10, 10), facecolor=PAPER)
    axes = figure.add_axes([0.12, 0.17, 0.76, 0.68], projection="polar")
    axes.set_facecolor(PAPER)
    axes.set_theta_zero_location("N")
    axes.set_theta_direction(-1)
    axes.set_ylim(0, inner_radius + scale_max + 40)

    axes.bar(angles, amounts, bottom=inner_radius, width=day_angle * 0.8,
             color=RAIN, edgecolor="none", zorder=3)
    axes.scatter(trace_angles, [inner_radius] * len(trace_angles),
                 s=8, color=TRACE, zorder=4)

    first_day = date(year, 1, 1)
    month_angles = []
    for month in range(1, 13):
        angle = (date(year, month, 1) - first_day).days * day_angle
        month_angles.append(angle)
        axes.plot([angle, angle], [inner_radius, inner_radius + scale_max],
                  color=GRID, linewidth=0.6, zorder=1)
    axes.set_xticks(month_angles, list(calendar.month_abbr)[1:])
    axes.tick_params(axis="x", colors=INK, labelsize=11, pad=8)
    axes.xaxis.grid(False)

    ticks = list(range(0, scale_max + 1, 100))
    axes.set_yticks([inner_radius + value for value in ticks],
                   [str(value) for value in ticks])
    axes.set_rlabel_position(75)
    axes.tick_params(axis="y", colors=INK, labelsize=9)
    axes.yaxis.grid(True, color=GRID, linewidth=0.7)
    axes.spines["polar"].set_visible(False)
    axes.text(0.5, 0.53, str(year), transform=axes.transAxes,
              ha="center", va="center", fontsize=26, weight="bold", color=INK)
    axes.text(0.5, 0.47, "Daily rainfall (mm)", transform=axes.transAxes,
              ha="center", va="center", fontsize=10, color=INK)

    figure.suptitle("Hong Kong Rainfall Fingerprint", y=0.95,
                   fontsize=21, weight="bold", color=INK)
    figure.text(0.5, 0.905, "January starts at the top; each day follows clockwise",
                ha="center", fontsize=10, color=INK)
    figure.legend(
        handles=[Patch(facecolor=RAIN, label="Bar length = daily rainfall (mm)"),
                 Line2D([], [], linestyle="none", marker="o", color=TRACE,
                        markersize=4, label="Trace: less than 0.05 mm")],
        loc="lower center", bbox_to_anchor=(0.5, 0.075), ncol=2,
        frameon=False, fontsize=10, labelcolor=INK,
    )
    figure.text(0.5, 0.04,
                f"Hong Kong Observatory station | {len(records)} days | Dry days have no bar",
                ha="center", fontsize=9, color=INK)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=200, facecolor=PAPER)
    plt.close(figure)


def main() -> None:
    try:
        records = load_year()
    except (OSError, ValueError) as problem:
        raise SystemExit(f"Could not read the saved rainfall data: {problem}") from None
    draw_fingerprint(records)
    measured = [(when, value) for when, value in records if value is not None]
    peak_day, peak_rain = max(measured, key=lambda record: record[1])
    trace_count = sum(value is None for _, value in records)
    print(f"Read {len(records)} days, including {trace_count} trace days.")
    print(f"Largest daily rainfall: {peak_rain:.1f} mm on {peak_day}.")
    print(f"Saved {OUTPUT.relative_to(HERE)}")


if __name__ == "__main__":
    main()

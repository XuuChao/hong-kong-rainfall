# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""Draw rainfall as straight lines that bend into arcs: uv run plot.py."""

import calendar
import csv
import math
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "data" / "daily_HKO_RF_ALL.csv"
OUTPUT = HERE / "out" / "rainfall-fingerprint-2025.png"
YEAR = 2025
PAPER = "#FAF8F4"
INK = "#183F4D"
RAIN = "#2A7886"
TRACE = "#8A9FA4"
GRID = "#D8D9D2"
PEAK = "#CB704B"
INNER_RADIUS = 150
TURN_MIN = 870
TURN_MAX = 950
LENGTH_PER_MM = 8


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


def path_parts(rainfall: float, turn_radius: float, length_per_mm: float) -> tuple[float, float]:
    """Return the straight endpoint and arc angle, preserving total path length."""
    length = rainfall * length_per_mm
    straight_length = min(length, turn_radius - INNER_RADIUS)
    arc_length = length - straight_length
    return INNER_RADIUS + straight_length, arc_length / turn_radius


def path_layout(records: list[tuple[date, float | None]]) -> tuple[float, dict[date, float]]:
    """Use one length scale, with separate outer tracks for the long paths."""
    largest = max(value for _, value in records if value is not None)
    if largest <= 0:
        return 1.0, {}
    # Keep the scale fixed so a larger outer circle gives more straight space.
    length_per_mm = min(
        LENGTH_PER_MM, (TURN_MAX - INNER_RADIUS + math.tau * TURN_MAX) / largest
    )
    long_days = sorted(
        ((when, value) for when, value in records
         if value is not None and value * length_per_mm > TURN_MIN - INNER_RADIUS),
        key=lambda record: (record[1], record[0]),
    )
    tracks = {}
    for index, (when, value) in enumerate(long_days):
        fraction = index / max(1, len(long_days) - 1)
        track = TURN_MIN + fraction * (TURN_MAX - TURN_MIN)
        # Even very similar extreme values must fit within one turn.
        minimum_radius = (value * length_per_mm + INNER_RADIUS) / (1 + math.tau)
        tracks[when] = max(track, minimum_radius)
    return length_per_mm, tracks


def draw_fingerprint(records: list[tuple[date, float | None]]) -> None:
    """Keep each day's angle; magnify its path and bend excess length clockwise."""
    year = records[0][0].year
    day_angle = math.tau / len(records)
    length_per_mm, tracks = path_layout(records)
    measured = [(when, value) for when, value in records if value is not None]
    peak_day, peak_rain = max(measured, key=lambda record: record[1])
    peak_label = f"{peak_day.day} {calendar.month_abbr[peak_day.month]}: {peak_rain:.1f} mm"
    figure = plt.figure(figsize=(12, 12), facecolor=PAPER)
    axes = figure.add_axes([0.075, 0.12, 0.85, 0.80], projection="polar")
    axes.set_facecolor(PAPER)
    axes.set_theta_zero_location("N")
    axes.set_theta_direction(-1)
    axes.set_ylim(0, TURN_MAX + 45)

    for index, (when, rainfall) in enumerate(records):
        angle = index * day_angle
        if rainfall is None:
            # This inward tick is a category marker, not an invented amount.
            axes.plot([angle, angle], [INNER_RADIUS - 14, INNER_RADIUS - 4],
                      color=TRACE, linewidth=0.8, solid_capstyle="butt", zorder=3)
            continue
        if rainfall == 0:
            continue
        turn_radius = tracks.get(when, TURN_MIN)
        endpoint, arc_angle = path_parts(rainfall, turn_radius, length_per_mm)
        color = PEAK if when == peak_day else RAIN
        width = 1.1 if when == peak_day else 0.8
        level = 5 if when == peak_day else 4
        axes.plot([angle, angle], [INNER_RADIUS, endpoint], color=color,
                  linewidth=width, solid_capstyle="butt", zorder=level)
        if arc_angle > 0:
            steps = max(2, math.ceil(arc_angle / 0.005))
            arc_angles = [angle + arc_angle * step / steps for step in range(steps + 1)]
            axes.plot(arc_angles, [turn_radius] * len(arc_angles), color=color,
                      linewidth=width, solid_capstyle="butt", zorder=level)

    first_day = date(year, 1, 1)
    month_angles = []
    for month in range(1, 13):
        angle = (date(year, month, 1) - first_day).days * day_angle
        month_angles.append(angle)
        axes.plot([angle, angle], [INNER_RADIUS, TURN_MIN],
                  color=GRID, linewidth=0.4, alpha=0.55, zorder=1)
    axes.set_xticks(month_angles, list(calendar.month_abbr)[1:])
    axes.tick_params(axis="x", colors=INK, labelsize=12, pad=8)
    axes.xaxis.grid(False)

    ticks = [0, 25, 50, 75]
    axes.set_yticks([INNER_RADIUS + value * length_per_mm for value in ticks],
                   ["", "25", "50", "75 mm"])
    axes.set_rlabel_position(75)
    axes.tick_params(axis="y", colors=INK, labelsize=9)
    axes.yaxis.grid(True, color=GRID, linewidth=0.5, alpha=0.7)
    axes.spines["polar"].set_visible(False)
    axes.text(0.5, 0.5, str(year), transform=axes.transAxes,
              ha="center", va="center", fontsize=22, weight="bold", color=INK)

    figure.suptitle("Hong Kong Rainfall", y=0.975,
                   fontsize=21, weight="bold", color=INK)
    figure.legend(
        handles=[Line2D([], [], color=RAIN, linewidth=1, label="Rainfall"),
                 Line2D([], [], color=PEAK, linewidth=1, label=peak_label),
                 Line2D([], [], linestyle="none", marker="|", color=TRACE,
                        markersize=5, label="Trace < 0.05 mm")],
        loc="lower center", bbox_to_anchor=(0.5, 0.055), ncol=3,
        frameon=False, fontsize=10, labelcolor=INK,
    )
    figure.text(0.5, 0.025, "Hong Kong Observatory",
                ha="center", fontsize=9, color=INK)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=300, facecolor=PAPER)
    figure.savefig(OUTPUT.with_suffix(".svg"), facecolor=PAPER)
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
    print(f"Saved {OUTPUT.with_suffix('.svg').relative_to(HERE)}")


if __name__ == "__main__":
    main()

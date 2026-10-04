# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Save the original HKO rainfall CSV once. Run with: uv run fetch.py."""

from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


HERE = Path(__file__).resolve().parent
SOURCE = (
    "https://data.weather.gov.hk/weatherAPI/cis/csvfile/"
    "HKO/ALL/daily_HKO_RF_ALL.csv"
)
SNAPSHOT = HERE / "data" / "daily_HKO_RF_ALL.csv"


def fetch_once() -> None:
    """Keep the publisher's bytes unchanged, and reuse an existing snapshot."""
    if SNAPSHOT.exists():
        print(f"Using existing snapshot: {SNAPSHOT.relative_to(HERE)}")
        return

    request = Request(SOURCE, headers={"User-Agent": "hong-kong-rainfall/1.0"})
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read()
    except (URLError, OSError) as problem:
        raise SystemExit(f"Could not download the rainfall file: {problem}") from None

    title = b"Daily Total Rainfall (mm) at the Hong Kong Observatory"
    if title not in raw.splitlines()[:2]:
        raise SystemExit("The response is not the expected HKO rainfall CSV; nothing saved.")

    try:
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        with SNAPSHOT.open("xb") as handle:
            handle.write(raw)
    except FileExistsError:
        print(f"Using existing snapshot: {SNAPSHOT.relative_to(HERE)}")
        return
    except OSError as problem:
        raise SystemExit(f"Could not save the rainfall file: {problem}") from None

    print(f"Saved {len(raw):,} unchanged bytes to {SNAPSHOT.relative_to(HERE)}")


if __name__ == "__main__":
    fetch_once()

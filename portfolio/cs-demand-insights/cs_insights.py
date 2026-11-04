"""Synthetic CS forecasting and contact-driver analysis; not Netflix data."""
from __future__ import annotations
import argparse
import csv
from collections import Counter
from pathlib import Path

def overlay_forecast(baseline: float, event_uplift: float, deflection: float) -> int:
    if baseline < 0 or event_uplift < -1 or not 0 <= deflection <= 1:
        raise ValueError("Invalid baseline, uplift, or deflection")
    return round(baseline * (1 + event_uplift) * (1 - deflection))

def forecast_quality(forecasts: list[float], actuals: list[float]) -> dict[str, float]:
    if len(forecasts) != len(actuals) or not actuals:
        raise ValueError("Forecast and actual arrays must have the same nonzero length")
    if any(x < 0 for x in forecasts + actuals):
        raise ValueError("Demand cannot be negative")
    total = sum(actuals)
    if total == 0:
        raise ValueError("WAPE and bias undefined for zero total actual demand")
    return {
        "wape": sum(abs(a - f) for f, a in zip(forecasts, actuals)) / total,
        "signed_bias": sum(f - a for f, a in zip(forecasts, actuals)) / total,
    }

def summarize_drivers(csv_path: str | Path) -> list[tuple[str, int, float]]:
    counts: Counter[str] = Counter()
    with open(csv_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            driver, count = row["driver"].strip(), int(row["contacts"])
            if not driver or count < 0:
                raise ValueError("Invalid contact record")
            counts[driver] += count
    total = sum(counts.values())
    if not total:
        raise ValueError("No contacts in input")
    return [(name, count, count / total) for name, count in counts.most_common()]

def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic CS demand insights")
    parser.add_argument("--data", default=str(Path(__file__).with_name("synthetic_contacts.csv")))
    args = parser.parse_args()
    print("SYNTHETIC DEMONSTRATION — NOT NETFLIX OR REAL CUSTOMER DATA")
    for label, uplift, deflection in [("Low", .05, .10), ("Central", .12, .08), ("High", .20, .05)]:
        print(label, overlay_forecast(10000, uplift, deflection), "contacts")
    metrics = forecast_quality([920, 1030, 1100], [1000, 1000, 1200])
    print("WAPE:", f"{metrics['wape']:.1%}", "Bias:", f"{metrics['signed_bias']:.1%}")
    for name, count, share in summarize_drivers(args.data):
        print(f"{name}: {count} ({share:.1%})")

if __name__ == "__main__":
    main()

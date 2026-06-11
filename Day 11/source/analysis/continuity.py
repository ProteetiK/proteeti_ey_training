import numpy as np
import pandas as pd

from pathlib import Path


def check_time_continuity(
    df: pd.DataFrame,
    timestamp_col: str,
    output_file: Path
):

    report = {}

    ts = df[timestamp_col].sort_values()

    delta = ts.diff().dropna()

    expected_interval = delta.median()

    report["expected_interval_ms"] = float(expected_interval)
    report["mean_interval_ms"] = float(delta.mean())
    report["std_interval_ms"] = float(delta.std())
    report["min_interval_ms"] = float(delta.min())
    report["max_interval_ms"] = float(delta.max())

    gaps = delta[delta > expected_interval * 1.5]

    report["gap_count"] = int(len(gaps))

    report["gap_duration_ms"] = float(gaps.sum())

    repeated = ts.duplicated().sum()

    report["repeated_timestamp_count"] = int(repeated)

    non_monotonic = (ts.diff() < 0).sum()

    report["non_monotonic_count"] = int(non_monotonic)

    continuity_df = pd.DataFrame([report])

    continuity_df.to_csv(output_file, index=False)

    return report
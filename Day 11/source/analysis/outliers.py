import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import zscore
from sklearn.ensemble import IsolationForest


def detect_zscore_outliers(series):

    z = np.abs(zscore(series.dropna()))

    idx = series.dropna().index[z > 3]

    return idx


def detect_iqr_outliers(series):

    q1 = series.quantile(0.25)

    q3 = series.quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr

    upper = q3 + 1.5 * iqr

    return series[
        (series < lower) |
        (series > upper)
    ].index


def detect_isolation_forest(series):

    clean = series.dropna()

    model = IsolationForest(
        contamination=0.01,
        random_state=42
    )

    pred = model.fit_predict(
        clean.values.reshape(-1,1)
    )

    return clean.index[pred == -1]


def create_outlier_plot(
    df,
    timestamp_col,
    signal,
    outlier_idx,
    output_file
):

    plt.figure(figsize=(15,6))

    plt.plot(
        df[timestamp_col],
        df[signal]
    )

    plt.scatter(
        df.loc[outlier_idx, timestamp_col],
        df.loc[outlier_idx, signal]
    )

    plt.title(
        f"{signal} Outliers"
    )

    plt.tight_layout()

    plt.savefig(output_file)

    plt.close()
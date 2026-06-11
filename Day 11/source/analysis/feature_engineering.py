import pandas as pd
import numpy as np

from scipy.fft import fft


def add_time_features(
    df,
    datetime_col
):

    df["hour"] = df[datetime_col].dt.hour

    df["minute"] = df[datetime_col].dt.minute

    df["second"] = df[datetime_col].dt.second

    df["millisecond"] = (
        df[datetime_col]
        .dt.microsecond // 1000
    )

    df["day"] = df[datetime_col].dt.day

    df["week"] = (
        df[datetime_col]
        .dt.isocalendar()
        .week
    )

    df["month"] = df[datetime_col].dt.month

    df["quarter"] = df[datetime_col].dt.quarter

    return df


def add_signal_features(
    df,
    signal
):

    lags = [
        1,2,3,5,10,20,50
    ]

    for lag in lags:

        df[
            f"{signal}_lag_{lag}"
        ] = df[signal].shift(lag)

    windows = [
        5,10,20,50,100
    ]

    for w in windows:

        df[
            f"{signal}_rolling_mean_{w}"
        ] = (
            df[signal]
            .rolling(w)
            .mean()
        )

        df[
            f"{signal}_rolling_std_{w}"
        ] = (
            df[signal]
            .rolling(w)
            .std()
        )

    df[
        f"{signal}_diff1"
    ] = df[signal].diff()

    df[
        f"{signal}_diff2"
    ] = df[signal].diff(2)

    df[
        f"{signal}_pct_change"
    ] = df[signal].pct_change()

    return df


def create_feature_inventory(df):

    rows = []

    for c in df.columns:

        rows.append({
            "Feature Name": c,
            "Feature Type": str(df[c].dtype),
            "Description":
                "Auto Generated"
        })

    return pd.DataFrame(rows)
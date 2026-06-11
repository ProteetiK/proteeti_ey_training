import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.fft import fft, fftfreq
from statsmodels.tsa.seasonal import seasonal_decompose


def estimate_sampling_interval_seconds(df, timestamp_col):

    delta = (
        df[timestamp_col]
        .diff()
        .dropna()
        .median()
    )

    return delta / 1000.0


def fft_period_detection(
    series,
    sampling_interval_seconds
):

    x = series.dropna().values

    n = len(x)

    yf = fft(x)

    xf = fftfreq(
        n,
        sampling_interval_seconds
    )

    mask = xf > 0

    xf = xf[mask]

    power = np.abs(yf[mask])

    idx = np.argmax(power)

    dominant_frequency = xf[idx]

    if dominant_frequency == 0:
        dominant_period = np.nan
    else:
        dominant_period = 1 / dominant_frequency

    return {
        "dominant_frequency": float(dominant_frequency),
        "dominant_period": float(dominant_period)
    }


def select_decomposition_period(
    series,
    candidate_periods=(10,20,30,50,100)
):

    n = len(series)

    valid = []

    for p in candidate_periods:

        if n >= p * 2:
            valid.append(p)

    if not valid:
        return None

    return valid[0]


def seasonal_analysis(
    series,
    signal_name,
    output_file
):

    period = select_decomposition_period(series)

    result_dict = {
        "period": None,
        "seasonal_strength": None,
        "trend_strength": None,
        "residual_strength": None
    }

    if period is None:

        return result_dict

    try:

        decomposition = seasonal_decompose(
            series.dropna(),
            period=period,
            model="additive"
        )

        fig = decomposition.plot()

        fig.set_size_inches(14,10)

        plt.savefig(output_file)

        plt.close()

        seasonal_var = np.var(
            decomposition.seasonal.dropna()
        )

        trend_var = np.var(
            decomposition.trend.dropna()
        )

        resid_var = np.var(
            decomposition.resid.dropna()
        )

        total = (
            seasonal_var +
            trend_var +
            resid_var
        )

        result_dict = {
            "period": period,
            "seasonal_strength":
                seasonal_var / total if total else 0,
            "trend_strength":
                trend_var / total if total else 0,
            "residual_strength":
                resid_var / total if total else 0
        }

    except Exception:

        pass

    return result_dict
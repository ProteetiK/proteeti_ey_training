import pandas as pd

from statsmodels.tsa.stattools import (
    adfuller,
    kpss
)


def run_adf(series):

    result = adfuller(
        series.dropna()
    )

    return {
        "adf_stat": result[0],
        "p_value": result[1]
    }


def run_kpss(series):

    try:

        result = kpss(
            series.dropna(),
            regression="c"
        )

        return {
            "kpss_stat": result[0],
            "p_value": result[1]
        }

    except:

        return {
            "kpss_stat": None,
            "p_value": None
        }


def determine_stationarity(
    adf_p,
    kpss_p
):

    if (
        adf_p < 0.05 and
        kpss_p > 0.05
    ):
        return "Stationary"

    return "Non-Stationary"


def minimum_differencing(series):

    current = series.copy()

    for d in [0,1,2]:

        adf = run_adf(current)

        kpss_res = run_kpss(current)

        if (
            adf["p_value"] < 0.05 and
            (
                kpss_res["p_value"] is None or
                kpss_res["p_value"] > 0.05
            )
        ):
            return d

        current = current.diff().dropna()

    return 2
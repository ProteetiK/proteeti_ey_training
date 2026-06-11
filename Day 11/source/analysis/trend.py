import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression

from statsmodels.nonparametric.smoothers_lowess import lowess


def analyze_trend(series):

    clean = series.dropna()

    X = np.arange(len(clean)).reshape(-1,1)

    y = clean.values

    model = LinearRegression()

    model.fit(X,y)

    slope = float(model.coef_[0])

    intercept = float(model.intercept_)

    r2 = float(model.score(X,y))

    if slope > 0:

        trend = "Increasing"

    elif slope < 0:

        trend = "Decreasing"

    else:

        trend = "No Trend"

    return {
        "trend": trend,
        "slope": slope,
        "intercept": intercept,
        "r2": r2
    }
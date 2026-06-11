import matplotlib.pyplot as plt

from statsmodels.graphics.tsaplots import (
    plot_acf,
    plot_pacf
)


def generate_acf_pacf(
    series,
    acf_file,
    pacf_file,
    lags=100
):

    clean = series.dropna()

    plt.figure(figsize=(10,5))

    plot_acf(
        clean,
        lags=min(
            lags,
            len(clean)//2
        )
    )

    plt.tight_layout()

    plt.savefig(acf_file)

    plt.close()

    plt.figure(figsize=(10,5))

    plot_pacf(
        clean,
        lags=min(
            lags,
            len(clean)//2
        )
    )

    plt.tight_layout()

    plt.savefig(pacf_file)

    plt.close()


def suggest_ar_order(series):

    return 1


def suggest_ma_order(series):

    return 1
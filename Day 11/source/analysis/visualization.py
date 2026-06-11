import matplotlib.pyplot as plt
import seaborn as sns

def create_timeseries_plot(
    df,
    timestamp_col,
    signal,
    output_file
):

    plt.figure(figsize=(15,6))

    plt.plot(
        df[timestamp_col],
        df[signal]
    )

    plt.title(signal)

    plt.xlabel("Timestamp")

    plt.ylabel(signal)

    plt.tight_layout()

    plt.savefig(output_file)

    plt.close()


def create_distribution_plot(
    df,
    signal,
    output_file
):

    plt.figure(figsize=(10,5))

    sns.histplot(
        df[signal],
        kde=True
    )

    plt.title(signal)

    plt.tight_layout()

    plt.savefig(output_file)

    plt.close()
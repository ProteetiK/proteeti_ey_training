import pandas as pd
import numpy as np
import missingno as msno
import matplotlib.pyplot as plt


def missing_value_analysis(
    df,
    output_csv,
    heatmap_png,
    matrix_png
):

    rows = []

    for col in df.columns:

        missing_count = df[col].isna().sum()

        missing_pct = (
            missing_count /
            len(df)
        ) * 100

        rows.append({
            "Column": col,
            "Missing Count": missing_count,
            "Missing %": round(missing_pct, 4)
        })

    report_df = pd.DataFrame(rows)

    report_df.to_csv(output_csv, index=False)

    plt.figure(figsize=(12,6))
    msno.heatmap(df)
    plt.savefig(
        heatmap_png,
        bbox_inches="tight"
    )
    plt.close()

    plt.figure(figsize=(12,6))
    msno.matrix(df)
    plt.savefig(
        matrix_png,
        bbox_inches="tight"
    )
    plt.close()

    return report_df


def impute_missing(df, report_df):

    df2 = df.copy()

    strategy_report = []

    for col in df2.columns:

        pct = report_df.loc[
            report_df["Column"] == col,
            "Missing %"
        ].values[0]

        strategy = None
        reason = None

        if pct < 1:

            df2[col] = df2[col].ffill()

            strategy = "Forward Fill"

            reason = "<1% Missing"

        elif pct <= 5:

            df2[col] = (
                df2[col]
                .interpolate(method="linear")
            )

            strategy = "Linear Interpolation"

            reason = "1%-5% Missing"

        elif pct <= 20:

            strategy = "Time Interpolation"

            reason = "5%-20% Missing"

        else:

            strategy = "Manual Review"

            reason = ">20% Missing"

        strategy_report.append({
            "Column": col,
            "Strategy Used": strategy,
            "Reason": reason
        })

    return df2, pd.DataFrame(strategy_report)
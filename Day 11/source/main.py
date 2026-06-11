import sys
import json
import warnings
import pandas as pd
import numpy as np

from pathlib import Path

from config import *

from analysis.continuity import check_time_continuity

from analysis.missing import (
    missing_value_analysis,
    impute_missing
)

from analysis.visualization import (
    create_timeseries_plot,
    create_distribution_plot
)

from analysis.trend import analyze_trend

from analysis.seasonality import (
    estimate_sampling_interval_seconds,
    fft_period_detection,
    seasonal_analysis
)

from analysis.outliers import (
    detect_zscore_outliers,
    detect_iqr_outliers,
    detect_isolation_forest,
    create_outlier_plot
)

from analysis.stationarity import (
    run_adf,
    run_kpss,
    determine_stationarity,
    minimum_differencing
)

from analysis.acf_pacf import (
    generate_acf_pacf,
    suggest_ar_order,
    suggest_ma_order
)

from analysis.feature_engineering import (
    add_time_features,
    add_signal_features,
    create_feature_inventory
)

from reporting.markdown_report import (
    generate_markdown_report
)

from reporting.summary_json import (
    save_summary
)

warnings.filterwarnings("ignore")

def build_datetime_column(df):

    df["datetime"] = pd.to_datetime(
        df[TIMESTAMP_COLUMN],
        unit="ms"
    )

    df = df.sort_values(
        TIMESTAMP_COLUMN
    ).reset_index(drop=True)

    return df


def run_continuity(df):

    print("Running continuity check...")

    report = check_time_continuity(
        df,
        TIMESTAMP_COLUMN,
        TABLES_DIR /
        "time_continuity_report.csv"
    )

    return report


def run_missing(df):

    print("Running missing value analysis...")

    missing_df = missing_value_analysis(
        df,
        TABLES_DIR /
        "missing_value_report.csv",
        PLOTS_DIR /
        "missing_heatmap.png",
        PLOTS_DIR /
        "missing_matrix.png"
    )

    df_imputed, strategy_df = impute_missing(
        df,
        missing_df
    )

    strategy_df.to_csv(
        TABLES_DIR /
        "missing_strategy_report.csv",
        index=False
    )

    df_imputed.to_csv(
        OUTPUT_DIR /
        "imputed_dataset.csv",
        index=False
    )

    return df_imputed, missing_df, strategy_df


def run_visualizations(df):

    print("Generating visualizations...")

    generated = []

    for signal in SIGNAL_COLUMNS:

        ts_file = (
            PLOTS_DIR /
            f"timeseries_{signal}.png"
        )

        create_timeseries_plot(
            df,
            "datetime",
            signal,
            ts_file
        )

        generated.append(str(ts_file))

        dist_file = (
            PLOTS_DIR /
            f"distribution_{signal}.png"
        )

        create_distribution_plot(
            df,
            signal,
            dist_file
        )

        generated.append(str(dist_file))

    return generated


def run_trend_analysis(df):

    print("Running trend analysis...")

    rows = []

    summary = {}

    for signal in SIGNAL_COLUMNS:

        result = analyze_trend(
            df[signal]
        )

        rows.append({
            "Column": signal,
            "Trend Direction":
                result["trend"],
            "Trend Strength":
                result["r2"],
            "Slope":
                result["slope"],
            "Intercept":
                result["intercept"]
        })

        summary[signal] = result

    trend_df = pd.DataFrame(rows)

    trend_df.to_csv(
        TABLES_DIR /
        "trend_report.csv",
        index=False
    )

    return summary


def run_seasonality(df):

    print("Running seasonality analysis...")

    sampling_interval = (
        estimate_sampling_interval_seconds(
            df,
            TIMESTAMP_COLUMN
        )
    )

    rows = []

    summary = {}

    for signal in SIGNAL_COLUMNS:

        fft_result = fft_period_detection(
            df[signal],
            sampling_interval
        )

        decomp = seasonal_analysis(
            df[signal],
            signal,
            PLOTS_DIR /
            f"decomposition_{signal}.png"
        )

        row = {
            "Column": signal,
            "Dominant Frequency":
                fft_result["dominant_frequency"],
            "Dominant Period":
                fft_result["dominant_period"],
            "Seasonal Strength":
                decomp["seasonal_strength"],
            "Trend Strength":
                decomp["trend_strength"]
        }

        rows.append(row)

        summary[signal] = row

    seasonality_df = pd.DataFrame(rows)

    seasonality_df.to_csv(
        TABLES_DIR /
        "trend_seasonality_report.csv",
        index=False
    )

    return summary


def run_outlier_analysis(df):

    print("Running outlier analysis...")

    all_rows = []

    for signal in SIGNAL_COLUMNS:

        z_idx = detect_zscore_outliers(
            df[signal]
        )

        iqr_idx = detect_iqr_outliers(
            df[signal]
        )

        iso_idx = detect_isolation_forest(
            df[signal]
        )

        combined = (
            set(z_idx)
            |
            set(iqr_idx)
            |
            set(iso_idx)
        )

        create_outlier_plot(
            df,
            "datetime",
            signal,
            list(combined),
            PLOTS_DIR /
            f"outliers_{signal}.png"
        )

        for idx in combined:

            all_rows.append({
                "Timestamp":
                    df.loc[idx, "datetime"],
                "Signal": signal,
                "Value":
                    df.loc[idx, signal]
            })

    outlier_df = pd.DataFrame(all_rows)

    outlier_df.to_csv(
        TABLES_DIR /
        "outlier_report.csv",
        index=False
    )

    return outlier_df


def run_stationarity(df):

    print("Running stationarity tests...")

    rows = []

    summary = {}

    for signal in SIGNAL_COLUMNS:

        adf = run_adf(
            df[signal]
        )

        kpss = run_kpss(
            df[signal]
        )

        stationarity = (
            determine_stationarity(
                adf["p_value"],
                kpss["p_value"]
            )
        )

        d = minimum_differencing(
            df[signal]
        )

        row = {
            "Column": signal,
            "ADF Statistic":
                adf["adf_stat"],
            "ADF p-value":
                adf["p_value"],
            "KPSS Statistic":
                kpss["kpss_stat"],
            "KPSS p-value":
                kpss["p_value"],
            "Stationary":
                stationarity,
            "Differencing Required":
                d
        }

        rows.append(row)

        summary[signal] = row

    stationarity_df = pd.DataFrame(rows)

    stationarity_df.to_csv(
        TABLES_DIR /
        "stationarity_report.csv",
        index=False
    )

    return summary


def run_acf_pacf(df):

    print("Generating ACF/PACF...")

    summary = {}

    for signal in SIGNAL_COLUMNS:

        generate_acf_pacf(
            df[signal],
            PLOTS_DIR /
            f"acf_{signal}.png",
            PLOTS_DIR /
            f"pacf_{signal}.png"
        )

        summary[signal] = {
            "p":
                suggest_ar_order(
                    df[signal]
                ),
            "q":
                suggest_ma_order(
                    df[signal]
                )
        }

    return summary


def run_feature_engineering(df):

    print("Running feature engineering...")

    df = add_time_features(
        df,
        "datetime"
    )

    for signal in SIGNAL_COLUMNS:

        df = add_signal_features(
            df,
            signal
        )

    feature_inventory = (
        create_feature_inventory(df)
    )

    feature_inventory.to_csv(
        TABLES_DIR /
        "feature_engineering_inventory.csv",
        index=False
    )

    df.to_csv(
        OUTPUT_DIR /
        "engineered_dataset.csv",
        index=False
    )

    return df, feature_inventory


def build_report(summary):

    report = {
        "Dataset Summary":
            summary["dataset"],
        "Continuity":
            summary["continuity"],
        "Trend":
            summary["trend"],
        "Seasonality":
            summary["seasonality"],
        "Stationarity":
            summary["stationarity"],
        "ACF PACF":
            summary["acf"]
    }

    generate_markdown_report(
        report,
        REPORT_DIR /
        "EDA_Report.md"
    )


def main(csv_path):

    print("\nLoading Dataset\n")

    df = pd.read_csv(csv_path)

    df = build_datetime_column(df)

    dataset_summary = {
        "rows":
            len(df),
        "columns":
            len(df.columns),
        "start":
            str(df["datetime"].min()),
        "end":
            str(df["datetime"].max())
    }

    continuity = run_continuity(df)

    df, missing_df, strategy_df = (
        run_missing(df)
    )

    generated_plots = (
        run_visualizations(df)
    )

    trend_summary = (
        run_trend_analysis(df)
    )

    seasonality_summary = (
        run_seasonality(df)
    )

    outlier_df = (
        run_outlier_analysis(df)
    )

    stationarity_summary = (
        run_stationarity(df)
    )

    acf_summary = (
        run_acf_pacf(df)
    )

    engineered_df, feature_inventory = (
        run_feature_engineering(df)
    )

    summary = {

        "dataset":
            dataset_summary,

        "continuity":
            continuity,

        "trend":
            trend_summary,

        "seasonality":
            seasonality_summary,

        "stationarity":
            stationarity_summary,

        "acf":
            acf_summary,

        "generated_plot_paths":
            generated_plots,

        "feature_engineering_columns":
            feature_inventory[
                "Feature Name"
            ].tolist()
    }

    build_report(summary)

    save_summary(
        summary,
        REPORT_DIR /
        "analysis_summary.json"
    )

    print(
        "\nPipeline completed successfully."
    )

    print(
        f"\nArtifacts saved in:\n{OUTPUT_DIR}"
    )


if __name__ == "__main__":

    csv_file = sys.argv[1]

    main(csv_file)
# Time Series EDA Report

## Dataset Summary

{'rows': 7423, 'columns': 7, 'start': '1970-01-01 00:02:15.093000', 'end': '1970-01-01 00:04:42.679000'}

## Continuity

{'expected_interval_ms': 20.0, 'mean_interval_ms': 19.88493667475074, 'std_interval_ms': 5.968155803734252, 'min_interval_ms': 0.0, 'max_interval_ms': 43.0, 'gap_count': 543, 'gap_duration_ms': 17906.0, 'repeated_timestamp_count': 54, 'non_monotonic_count': 0}

## Trend

{'red': {'trend': 'Decreasing', 'slope': -0.05353101937598095, 'intercept': 40965.46783895842, 'r2': 0.20541061499211632}, 'ir': {'trend': 'Decreasing', 'slope': -0.18437626120612535, 'intercept': 101002.09084285445, 'r2': 0.544616757898543}, 'red_corrected': {'trend': 'Increasing', 'slope': 0.0005230953712574852, 'intercept': 5.4490030905746245, 'r2': 0.0001602777230902408}, 'ir_corrected': {'trend': 'Increasing', 'slope': 0.009412539069231814, 'intercept': -57.018753635013425, 'r2': 0.011702840287508787}}

## Seasonality

{'red': {'Column': 'red', 'Dominant Frequency': 0.006735821096591674, 'Dominant Period': 148.46, 'Seasonal Strength': np.float64(1.9136148363476962e-06), 'Trend Strength': np.float64(0.9981819809201866)}, 'ir': {'Column': 'ir', 'Dominant Frequency': 0.006735821096591674, 'Dominant Period': 148.46, 'Seasonal Strength': np.float64(3.884890931089915e-07), 'Trend Strength': np.float64(0.9993057233944793)}, 'red_corrected': {'Column': 'red_corrected', 'Dominant Frequency': 0.013471642193183348, 'Dominant Period': 74.23, 'Seasonal Strength': np.float64(1.5985207186162114e-05), 'Trend Strength': np.float64(0.9849382382759546)}, 'ir_corrected': {'Column': 'ir_corrected', 'Dominant Frequency': 0.020207463289775022, 'Dominant Period': 49.48666666666667, 'Seasonal Strength': np.float64(3.426548721388041e-06), 'Trend Strength': np.float64(0.9942602564952499)}}

## Stationarity

{'red': {'Column': 'red', 'ADF Statistic': np.float64(-0.982644637759665), 'ADF p-value': np.float64(0.7595415245349939), 'KPSS Statistic': np.float64(4.272656732171617), 'KPSS p-value': np.float64(0.01), 'Stationary': 'Non-Stationary', 'Differencing Required': 1}, 'ir': {'Column': 'ir', 'ADF Statistic': np.float64(-1.5909135354020116), 'ADF p-value': np.float64(0.48815633644700446), 'KPSS Statistic': np.float64(8.230522166998647), 'KPSS p-value': np.float64(0.01), 'Stationary': 'Non-Stationary', 'Differencing Required': 1}, 'red_corrected': {'Column': 'red_corrected', 'ADF Statistic': np.float64(-2.544890543924178), 'ADF p-value': np.float64(0.10493039833755974), 'KPSS Statistic': np.float64(0.925961101450897), 'KPSS p-value': np.float64(0.01), 'Stationary': 'Non-Stationary', 'Differencing Required': 1}, 'ir_corrected': {'Column': 'ir_corrected', 'ADF Statistic': np.float64(-3.6294294599530312), 'ADF p-value': np.float64(0.005222693244950824), 'KPSS Statistic': np.float64(0.49497875060372193), 'KPSS p-value': np.float64(0.04279757869285543), 'Stationary': 'Non-Stationary', 'Differencing Required': 1}}

## ACF PACF

{'red': {'p': 1, 'q': 1}, 'ir': {'p': 1, 'q': 1}, 'red_corrected': {'p': 1, 'q': 1}, 'ir_corrected': {'p': 1, 'q': 1}}

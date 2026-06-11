from pathlib import Path

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"

PLOTS_DIR = OUTPUT_DIR / "plots"

TABLES_DIR = OUTPUT_DIR / "tables"

REPORT_DIR = OUTPUT_DIR / "reports"

for p in [OUTPUT_DIR, PLOTS_DIR, TABLES_DIR, REPORT_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# =========================================================
# SIGNALS
# =========================================================

SIGNAL_COLUMNS = [
    "red",
    "ir",
    "red_corrected",
    "ir_corrected"
]

TIMESTAMP_COLUMN = "timestamp_ms"

# =========================================================
# ANALYSIS PARAMETERS
# =========================================================

ROLLING_WINDOWS = [5, 10, 20, 50, 100]

TREND_WINDOWS = [50, 100, 500]

ACF_LAGS = 100
PACF_LAGS = 100

OUTLIER_ZSCORE_THRESHOLD = 3

ISOLATION_FOREST_CONTAMINATION = 0.01

RANDOM_STATE = 42
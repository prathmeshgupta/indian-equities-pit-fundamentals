"""Point-in-Time Fundamentals Weekly Dataset Updater.

Fetches updated quarterly financial statement filings and point-in-time
effective dates for Indian equities, deduplicating records and updating
both CSV and Apache Parquet datasets.
"""

import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

# Add local src to path for direct execution
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from indian_equities_pit_fundamentals.fetcher import FundamentalsFetcher

SYMBOLS_TO_TRACK = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "INFY",
    "ICICIBANK",
    "BHARTIARTL",
    "ITC",
    "LT",
    "SBIN",
    "HINDUNILVR"
]

def update_pit_fundamentals():
    print(f"[{datetime.now().isoformat()}] Starting Point-in-Time Fundamentals update...")
    fetcher = FundamentalsFetcher()
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_file = output_dir / "pit_fundamentals.csv"
    parquet_file = output_dir / "pit_fundamentals.parquet"

    existing_df = pd.DataFrame()
    if csv_file.exists():
        existing_df = pd.read_csv(csv_file)
        print(f"Loaded {len(existing_df)} existing records from {csv_file.name}")

    # 1. Fetch quarterly statements for tracked symbols
    all_new_records = []
    for sym in SYMBOLS_TO_TRACK:
        try:
            print(f"Fetching quarterly statements for {sym}...")
            df_sym = fetcher.fetch_historical_quarterly_yfinance(sym)
            if not df_sym.empty:
                all_new_records.append(df_sym)
        except Exception as e:
            print(f"Warning: Failed to fetch quarterly statements for {sym}: {e}")

    # 2. Attempt fetching live filings from NSE
    try:
        live_df = fetcher.fetch_live_filings()
        if not live_df.empty:
            print(f"Retrieved {len(live_df)} live filing records from NSE.")
            all_new_records.append(live_df)
    except Exception as e:
        print(f"Notice: Live NSE filings fetch skipped or unavailable: {e}")

    if not all_new_records and existing_df.empty:
        raise RuntimeError("No fundamentals data retrieved and no existing data found.")

    # Combine
    combined = list(all_new_records)
    if not existing_df.empty:
        combined.insert(0, existing_df)

    merged = pd.concat(combined, ignore_index=True)

    # Ensure required columns
    for col in ["revenue", "net_income", "ebitda", "eps", "stockholders_equity"]:
        if col not in merged.columns:
            merged[col] = None

    # Deduplicate keeping last, by symbol and period_ended
    merged["period_ended"] = merged["period_ended"].astype(str)
    merged["symbol"] = merged["symbol"].astype(str).str.upper()
    merged = merged.drop_duplicates(subset=["symbol", "period_ended"], keep="last")

    # Sort deterministically
    merged = merged.sort_values(by=["symbol", "period_ended"], ascending=[True, False]).reset_index(drop=True)

    if "created_at" not in merged.columns or merged["created_at"].isnull().any():
        merged["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save
    merged.to_csv(csv_file, index=False)
    merged.to_parquet(parquet_file, index=False)

    print(f"Saved {len(merged)} records to {csv_file.name} and {parquet_file.name}")

    # Run quick validation
    from evaluate_quality import audit_quality
    audit_quality()
    print("Point-in-Time Fundamentals update completed successfully.")

if __name__ == "__main__":
    update_pit_fundamentals()

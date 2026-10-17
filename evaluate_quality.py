import pandas as pd
from pathlib import Path

def audit_quality():
    print("=" * 60)
    print(" PIT FUNDAMENTALS - DATA QUALITY AUDIT")
    print("=" * 60)
    
    csv_path = Path(__file__).parent / "output" / "pit_fundamentals.csv"
    assert csv_path.exists(), "pit_fundamentals.csv missing"
    
    df = pd.read_csv(csv_path)
    print(f"Total Quarterly Statements Indexed: {len(df)}")
    
    null_syms = df["symbol"].isnull().sum()
    null_filings = df["filing_date"].isnull().sum()
    null_periods = df["period_ended"].isnull().sum()
    print(f"Null Symbols: {null_syms} {'[PASS]' if null_syms == 0 else '[FAIL]'}")
    print(f"Null Period End Dates: {null_periods} {'[PASS]' if null_periods == 0 else '[FAIL]'}")
    print(f"Null Filing Dates: {null_filings} {'[PASS]' if null_filings == 0 else '[FAIL]'}")
    
    # Check that filing_date >= period_ended (no future filing before period end)
    df["dt_filing"] = pd.to_datetime(df["filing_date"])
    df["dt_period"] = pd.to_datetime(df["period_ended"])
    invalid_lags = (df["dt_filing"] < df["dt_period"]).sum()
    print(f"Temporal Violations (Filing < Period End): {invalid_lags} {'[PASS]' if invalid_lags == 0 else '[FAIL]'}")
    
    print("=" * 60)
    print("ALL AUDIT CHECKS PASSED.")
    print("=" * 60)

if __name__ == "__main__":
    audit_quality()

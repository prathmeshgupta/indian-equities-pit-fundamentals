import argparse
import pandas as pd
from datetime import date
from pathlib import Path
from indian_equities_pit_fundamentals.aligner import PITAligner

def main():
    parser = argparse.ArgumentParser(description="Point-in-Time Fundamentals Agent")
    parser.add_argument("--symbol", help="Target equity ticker")
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Query as of date (YYYY-MM-DD)")
    args = parser.parse_args()

    csv_path = Path(__file__).parent / "output" / "pit_fundamentals.csv"
    if not csv_path.exists():
        print("Output file not found.")
        return

    df = pd.read_csv(csv_path)
    if args.symbol:
        aligner = PITAligner(df)
        res = aligner.get_latest_statement(args.symbol.upper(), args.as_of)
        print(f"\n--- Latest Filed Financials for {args.symbol} as of {args.as_of} ---")
        if res:
            for k, v in res.items():
                print(f"  • {k:<20}: {v}")
        else:
            print("  No statement was filed on or before this date.")
    else:
        print(f"Loaded {len(df)} financial filing statements. Use --symbol <TICKER> [--as-of YYYY-MM-DD].")

if __name__ == "__main__":
    main()

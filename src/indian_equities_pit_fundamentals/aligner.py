import pandas as pd
from typing import Optional, Dict

class PITAligner:
    """Enforces strict Point-in-Time queries: statement is visible ONLY IF filing_date <= query_date."""

    def __init__(self, df_fundamentals: pd.DataFrame):
        self.df = df_fundamentals.copy()
        if not self.df.empty:
            self.df["filing_date"] = pd.to_datetime(self.df["filing_date"]).dt.strftime("%Y-%m-%d")

    def get_latest_statement(self, symbol: str, query_date: str) -> Optional[Dict]:
        sub = self.df[(self.df["symbol"] == symbol) & (self.df["filing_date"] <= query_date)]
        if sub.empty:
            return None
        latest = sub.sort_values("filing_date", ascending=False).iloc[0]
        return latest.to_dict()

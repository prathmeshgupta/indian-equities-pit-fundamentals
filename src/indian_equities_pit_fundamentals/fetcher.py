import io
import requests
import pandas as pd
import numpy as np
from typing import Optional

NSE_FIN_RESULTS_URL = "https://www.nseindia.com/api/corporates-financial-results?index=equities"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

class FundamentalsFetcher:
    """Fetches quarterly financial results and filing dates from NSE and yfinance."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._primed = False

    def _prime_session(self):
        if not self._primed:
            self.session.get("https://www.nseindia.com", timeout=10)
            self._primed = True

    def fetch_live_filings(self) -> pd.DataFrame:
        self._prime_session()
        resp = self.session.get(NSE_FIN_RESULTS_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            return pd.DataFrame()

        rows = []
        for item in data:
            rows.append({
                "symbol": item.get("symbol"),
                "company_name": item.get("companyName"),
                "period_ended": item.get("to_date") or item.get("period_ended"),
                "filing_date": item.get("re_date") or item.get("filing_date"),
                "revenue": item.get("income"),
                "net_income": item.get("pat"),
                "eps": item.get("eps"),
                "source": "NSE_FINANCIALS_LIVE"
            })
        return pd.DataFrame(rows)

    def fetch_historical_quarterly_yfinance(self, symbol: str) -> pd.DataFrame:
        import yfinance as yf
        ticker_str = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
        t = yf.Ticker(ticker_str)
        fin = t.quarterly_financials
        bs = t.quarterly_balance_sheet
        records = []

        if not fin.empty:
            for period_dt in fin.columns:
                col_data = fin[period_dt]
                # In absence of exact board meeting timestamp, apply standard +45 day regulatory filing lag
                filing_dt = (period_dt + pd.Timedelta(days=45)).strftime("%Y-%m-%d")
                period_str = period_dt.strftime("%Y-%m-%d")

                revenue = col_data.get("Total Revenue", np.nan)
                net_income = col_data.get("Net Income", np.nan)
                ebitda = col_data.get("EBITDA", col_data.get("Operating Income", np.nan))

                equity = np.nan
                if not bs.empty and period_dt in bs.columns:
                    equity = bs[period_dt].get("Stockholders Equity", np.nan)

                records.append({
                    "symbol": symbol.replace(".NS", ""),
                    "period_ended": period_str,
                    "filing_date": filing_dt,
                    "revenue": float(revenue) if pd.notnull(revenue) else None,
                    "net_income": float(net_income) if pd.notnull(net_income) else None,
                    "ebitda": float(ebitda) if pd.notnull(ebitda) else None,
                    "stockholders_equity": float(equity) if pd.notnull(equity) else None,
                    "source": "YFINANCE_QUARTERLY"
                })

        return pd.DataFrame(records)

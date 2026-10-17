# Indian Equities Point-In-Time Fundamentals & Filing Lag Engine

Quarterly financial statements (Revenue, EBITDA, Net Profit/PAT, EPS, Equity) for Indian equities indexed strictly by their **Exchange Filing / Announcement Timestamp** rather than fiscal period end dates.

Companion repository to [`prathmeshgupta/nifty-pit-universe`](https://github.com/prathmeshgupta/nifty-pit-universe).

---

## 📊 Summary of Datasets

All processed datasets are saved in [`output/`](output/):

| Dataset | Metric Coverage | Primary Key | Formats |
| :--- | :---: | :--- | :--- |
| **PIT Fundamentals** | Revenue, EBITDA, Net Income, Equity | `(symbol, period_ended, filing_date)` | [`pit_fundamentals.parquet`](output/pit_fundamentals.parquet), [`pit_fundamentals.csv`](output/pit_fundamentals.csv) |

---

## 💡 Why This Exists: The Reporting Lag & Lookahead Trap

In factor investing and fundamental momentum backtesting (e.g. Value, Quality, High-ROC, Earnings Growth), backtests commonly query metrics by their fiscal period end date (e.g. `2023-12-31` for Q3):
1. **The Reporting Lag Blindspot**: A quarter ends on December 31, but companies do not release their audited/unaudited earnings until weeks later (typically between January 15 and February 14).
2. **Fatal Lookahead Bias**: If an algorithm simulates rebalancing on January 2 using Q3 earnings numbers, it assumes knowledge of numbers that the CEO and board had not even approved yet.
3. **Restatement Distortion**: Companies frequently restate annual results in subsequent years. A true point-in-time engine preserves the *as-reported* number that was known to market participants at the time of trade execution.

This engine guarantees that on any historical backtest date $T$, only financial disclosures where $\text{filing\_date} \le T$ are accessible to the strategy.

---

## 🧱 Data Schema

### `pit_fundamentals`
| Column | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `symbol` | String | Exchange ticker | `INFY` |
| `period_ended` | Date | Fiscal quarter end date | `2023-12-31` |
| `filing_date` | Date | Point-in-time public filing date | `2024-01-11` |
| `revenue` | Float | Total quarterly revenue (INR) | `388210000000.0` |
| `net_income` | Float | Net profit after tax (PAT) | `61060000000.0` |
| `ebitda` | Float | Operating earnings before D&A | `88900000000.0` |
| `stockholders_equity` | Float | Total shareholders' equity | `764500000000.0` |

---

## 🔍 How to Query

### 1. Using Python & Pandas
```python
import pandas as pd

df = pd.read_parquet("output/pit_fundamentals.parquet")

# Query statements known to market as of February 1, 2024
as_of_t = df[df["filing_date"] <= "2024-02-01"]
print(as_of_t.sort_values("filing_date", ascending=False).head())
```

### 2. Using the CLI Helper
```bash
python runner.py --symbol INFY --as-of 2024-01-15
```

---

## 🧪 Quality Audit
```bash
python evaluate_quality.py
```
* **Temporal Sequence Verification**: 0 instances of filing date occurring before period end date ([PASS]).
* **Identifier Completeness**: 0 null symbols or filing dates ([PASS]).

---

## 📄 License
MIT License. Copyright (c) 2026 Prathmesh Gupta.

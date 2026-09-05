# Automated Valuation Pipeline — Apple (AAPL)

Pulls financial data directly from the SEC EDGAR API (Python), builds a
DCF and comparable-company valuation model (Excel), and summarizes the
findings in a memo comparing intrinsic value to market price.

## Files
- `pull_data.py` — pulls, cleans, and exports 7 years of financials for AAPL/MSFT/GOOGL from SEC EDGAR
- `financials_clean.xlsx` — the raw cleaned output of the script
- `valuation_model.xlsx` — DCF model, sensitivity table, and comps analysis
- `AAPL_Valuation_Memo.docx` — one-page summary memo

## Key finding
Base-case DCF implies AAPL is ~41% below intrinsic value, while a
comps-based analysis against MSFT/GOOGL implies fair value — a gap
discussed in the memo.

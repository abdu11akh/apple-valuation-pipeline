import requests
import json
import pandas as pd
from datetime import date

HEADERS = {"User-Agent": "A Mirzaev amirzaevdev123@gmail.com"}

def get_cik_map():
    url = "https://www.sec.gov/files/company_tickers.json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    return {v["ticker"]: str(v["cik_str"]).zfill(10) for v in data.values()}

def get_company_facts(cik):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def extract_series(facts, tag_candidates, unit="USD"):
    combined = {}
    for tag in tag_candidates:
        try:
            entries = facts["facts"]["us-gaap"][tag]["units"][unit]
        except KeyError:
            continue
        for e in entries:
            days = (date.fromisoformat(e["end"]) - date.fromisoformat(e["start"])).days
            if days > 300:
                combined[e["end"]] = e  # keyed by end date, so overlapping years don't duplicate
    if not combined:
        return None
    return list(combined.values())
cik_map = get_cik_map()
tickers = ["AAPL", "MSFT", "GOOGL"]
all_data = []

for ticker in tickers:
    cik = cik_map[ticker]
    facts = get_company_facts(cik)
    revenue = extract_series(facts, ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"])
    for entry in revenue:
        all_data.append({
            "ticker": ticker,
            "fiscal_year": entry["fy"],
            "metric": "Revenue",
            "value": entry["val"]
        })

print(len(all_data))
print(all_data[0])


metrics_to_pull = {
    "Revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
    "NetIncome": ["NetIncomeLoss"],
    "OperatingIncome": ["OperatingIncomeLoss"],
}    

cik_map = get_cik_map()
tickers = ["AAPL", "MSFT", "GOOGL"]
all_data = []

for ticker in tickers:
    cik = cik_map[ticker]
    facts = get_company_facts(cik)
    for metric_name, tag_candidates in metrics_to_pull.items():
        series = extract_series(facts, tag_candidates)
        if series is None:
            print(f"Skipped {metric_name} for {ticker} — no matching tag found")
            continue
        for entry in series:
            all_data.append({
                "ticker": ticker,
                "fiscal_year": date.fromisoformat(entry["end"]).year,
                "metric": metric_name,
                "value": entry["val"],
                "filed": entry["filed"]
            })

print(len(all_data))


df = pd.DataFrame(all_data)
df["filed"] = pd.to_datetime(df["filed"])
df = df.sort_values("filed")
df = df.drop_duplicates(subset=["ticker", "fiscal_year", "metric"], keep="last")
print(df.head(10))
print(df.shape)
print(df[(df["ticker"] == "AAPL") & (df["metric"] == "NetIncome")].sort_values("fiscal_year"))


wide = df.pivot_table(index=["ticker", "fiscal_year"], columns="metric", values="value").reset_index()
print(wide.head(10))


wide.to_excel("data/financials_clean.xlsx", index=False)
print("Saved to data/financials_clean.xlsx")
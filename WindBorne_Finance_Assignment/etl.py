import requests
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from models import SessionLocal, Company, FinancialStatement, init_db

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

COMPANIES = [
    {"ticker": "TEL", "name": "TE Connectivity"},
    {"ticker": "ST", "name": "Sensata Technologies"},
    {"ticker": "DD", "name": "DuPont de Nemours"}
]

FUNCTIONS = {
    "INCOME_STATEMENT": "annualReports",
    "BALANCE_SHEET": "annualReports",
    "CASH_FLOW": "annualReports"
}

def fetch_data(function, symbol):
    """Fetch data from Alpha Vantage with rate limit handling."""
    params = {
        "function": function,
        "symbol": symbol,
        "apikey": API_KEY
    }
    
    # Check for local cache first to save API calls
    cache_dir = "data/raw"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = f"{cache_dir}/{symbol}_{function}.json"
    
    if os.path.exists(cache_file):
        print(f"Loading {symbol} {function} from cache...")
        with open(cache_file, "r") as f:
            return json.load(f)

    print(f"Fetching {symbol} {function} from API...")
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Save to cache
    if "Note" not in data and "Information" not in data:
         with open(cache_file, "w") as f:
            json.dump(data, f, indent=4)
    else:
        print(f"API Limit or Error for {symbol}: {data}")
        
    return data

def run_etl():
    init_db()
    session = SessionLocal()
    
    for company_info in COMPANIES:
        ticker = company_info["ticker"]
        
        # 1. Ensure Company exists
        company = session.query(Company).filter_by(ticker=ticker).first()
        if not company:
            company = Company(ticker=ticker, name=company_info["name"])
            session.add(company)
            session.commit()
            print(f"Created company: {ticker}")
        
        # 2. Fetch and Store Statements
        for func_name, json_key in FUNCTIONS.items():
            data = fetch_data(func_name, ticker)
            
            if json_key not in data:
                print(f"No data found for {ticker} {func_name}")
                continue
                
            reports = data[json_key]
            
            # We only want the last 3 years
            # API returns sorted by date usually, but let's be safe
            # Actually, let's just store everything we get, filtering can happen in analysis
            
            for report in reports:
                fiscal_date = datetime.strptime(report['fiscalDateEnding'], "%Y-%m-%d").date()
                
                # Check if exists
                exists = session.query(FinancialStatement).filter_by(
                    company_id=company.id,
                    statement_type=func_name,
                    fiscal_date_ending=fiscal_date
                ).first()
                
                if not exists:
                    stmt = FinancialStatement(
                        company_id=company.id,
                        statement_type=func_name,
                        fiscal_date_ending=fiscal_date,
                        data=report
                    )
                    session.add(stmt)
                    print(f"Added {func_name} for {ticker} - {fiscal_date}")
            
            session.commit()
            
            # Respect API rate limit (5 calls/min)
            # Since we cache, this only affects fresh fetches.
            time.sleep(12) 

    session.close()
    print("ETL Complete.")

if __name__ == "__main__":
    run_etl()

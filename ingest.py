import yfinance as yf
from db import insert_fund, insert_prices

TICKERS = ["VOO", "SPY", "BND"] # List of fund tickers to ingest

def ingest():
    for ticker in TICKERS:

        df = yf.download(ticker, period="max", interval="1d")
        df.columns = df.columns.droplevel(1)    # drops the Ticker level from the column headers
        df = df.reset_index()                   # turns the Date index into a regular "Date" column
        fund_id = insert_fund(ticker)
        insert_prices(fund_id, df)
        print(f"Loaded {len(df)} rows for {ticker}")

if __name__ == "__main__":
    ingest()
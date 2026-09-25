import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
# ========================== Stage 1: Fetch Data ==============================================

import yfinance as yf # pulls from Yahoo Finance
TICKER = "VOO"
df = yf.download(TICKER, period="max", interval="1d")
df.columns = df.columns.droplevel(1)    # drops the Ticker level from the column headers
df = df.reset_index()                   # turns the Date index into a regular "Date" column
print(df)

# ========================== Stage 2: Store Data ==============================================

def insert_fund(ticker):
    cur = conn.cursor()
    cur.execute("SELECT id FROM funds WHERE ticker = %s", (ticker,))
    result = cur.fetchone()
    if result:
        fund_id = result[0]
    else:
        cur.execute("INSERT INTO funds (ticker, name) VALUES (%s, %s) RETURNING id", (ticker, ticker))
        fund_id = cur.fetchone()[0]
        conn.commit()
    cur.close()
    return fund_id

def insert_prices(fund_id, df):
    cur = conn.cursor()
    for _, row in df.iterrows():
       cur.execute("INSERT into price_history(fund_id, price_date, close_price) VALUES (%s, %s, %s)", 
                   (fund_id, row["Date"], row["Close"]))
    conn.commit()
    cur.close()

fund_id = insert_fund(TICKER)
insert_prices(fund_id, df)
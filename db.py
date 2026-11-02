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

# ========================== Store Data ==============================================

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
       cur.execute(
           """INSERT INTO price_history (fund_id, price_date, close_price) 
              VALUES (%s, %s, %s)
              ON CONFLICT (fund_id, price_date) DO NOTHING""", 
           (fund_id, row["Date"], row["Close"])
       )
    conn.commit()
    cur.close()

def get_prices(fund_id): # fetch the price history for a given fund_id from the database
    cur = conn.cursor()
    cur.execute("SELECT price_date, close_price FROM price_history WHERE fund_id = %s ORDER BY price_date ASC", (fund_id,))
    rows = cur.fetchall() # returns a list of tuples
    cur.close()
    return rows

def get_funds():
    cur = conn.cursor()
    cur.execute("SELECT ...")   # ticker, name, expense_ratio, is_benchmark
    rows = cur.fetchall()
    cur.close()
    return rows
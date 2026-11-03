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

# ========================== Store Data in Database ==============================================

def insert_fund(ticker): # insert a fund into the database if it doesn't already exist, and return its id
    with conn:                                  # commit on success, rollback on error
        with conn.cursor() as cur:              # cursor closes automatically
            cur.execute("SELECT id FROM funds WHERE ticker = %s", (ticker,))
            result = cur.fetchone() # returns None if no rows are found, otherwise returns a tuple of the first row
            if result:
                return result[0]
            cur.execute(
                "INSERT INTO funds (ticker, name) VALUES (%s, %s) RETURNING id",
                (ticker, ticker),
            )
            return cur.fetchone()[0]

def insert_prices(fund_id, df): # insert price history for a given fund_id into the database
    with conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows(): # iterate over each row in the DataFrame
                cur.execute(
                    """INSERT INTO price_history (fund_id, price_date, close_price)
                       VALUES (%s, %s, %s)
                       ON CONFLICT (fund_id, price_date) DO NOTHING""",
                    (fund_id, row["Date"], row["Close"]),
                )

def get_prices(fund_id): # fetch the price history for a given fund_id from the database
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT price_date, close_price FROM price_history "
                "WHERE fund_id = %s ORDER BY price_date ASC",
                (fund_id,),
            )
            return cur.fetchall()

def get_funds(): # fetch all funds from the database
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ticker, name, expense_ratio, is_benchmark "
                "FROM funds ORDER BY ticker"
            )
            return cur.fetchall() 
        
def get_fund_id(ticker):
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM funds WHERE ticker = %s", (ticker,))
            row = cur.fetchone() # returns None if no rows are found, otherwise returns a tuple of the first row
            return row[0] if row else None # return the id if found, otherwise return None
        

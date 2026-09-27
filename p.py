import os
from dotenv import load_dotenv
import psycopg2
import statistics

load_dotenv()
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

import yfinance as yf # pulls from Yahoo Finance

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

# ========================== Fetch Data ==============================================

TICKERS = ["VOO", "SPY", "BND"]
for ticker in TICKERS:

    df = yf.download(ticker, period="max", interval="1d")
    df.columns = df.columns.droplevel(1)    # drops the Ticker level from the column headers
    df = df.reset_index()                   # turns the Date index into a regular "Date" column
    fund_id = insert_fund(ticker)
    insert_prices(fund_id, df)
    print(f"Loaded {len(df)} rows for {ticker}")

def get_prices(fund_id): # fetch the price history for a given fund_id from the database
    cur = conn.cursor()
    cur.execute("SELECT price_date, close_price FROM price_history WHERE fund_id = %s ORDER BY price_date ASC", (fund_id,))
    rows = cur.fetchall() # returns a list of tuples
    cur.close()
    return rows

# voo_prices = get_prices(3)  # VOO's fund_id
# print(voo_prices[:5])   # first 5 rows
# print(voo_prices[-5:])  # last 5 rows
# print(len(voo_prices))  # should be 4036

# compute the day-over-day % change:
def calculate_daily_returns(prices): # calculate the daily returns of a fund's price history
    returns = []
    for i in range(1, len(prices)):
        prev_price = prices[i-1][1]  # close_price of previous day
        curr_price = prices[i][1]    # close_price of current day
        daily_return = (curr_price - prev_price) / prev_price
        returns.append((prices[i][0], daily_return))  # (date, daily_return)
    return returns

# voo_prices = get_prices(3)
# voo_returns = calculate_daily_returns(voo_prices)
# print(len(voo_returns))       # should be 4035 (one less than voo_prices' 4036)
# print(voo_returns[:3])         # first few returns

def calculate_cumulative_returns(prices): # calculate the cumulative return of a fund's price history
    early_price = prices[0][1]  # close_price of the first day
    latest_price = prices[-1][1]  # close_price of the last day
    cumulative_return = (latest_price - early_price) / early_price
    return cumulative_return

# voo_prices = get_prices(3)
# voo_cumulative_return = calculate_cumulative_returns(voo_prices)
# print(voo_cumulative_return)  # should be the cumulative return for VOO

# Volatility measures how much a fund's daily returns bounce around. Decimal -> Float
# (252 ≈ the number of trading days in a year — this is a standard convention in finance, not something you calculate yourself.)

def calculate_volatility(daily_returns): # calculate the annualized volatility of a fund's daily returns
    daily_return_values = [float(r[1]) for r in daily_returns] # extract the daily return values as floats
    daily_std_dev = statistics.stdev(daily_return_values) # calculate the standard deviation of daily returns
    volatility = daily_std_dev * (252 ** 0.5) # annualized volatility = standard deviation of daily returns * sqrt(252)
    return volatility

# voo_prices = get_prices(3)
# voo_returns = calculate_daily_returns(voo_prices)  # <- this step was missing
# voo_volatility = calculate_volatility(voo_returns)
# print(voo_volatility)  # should be the annualized volatility for VOO

def calculate_annualized_return(prices): # calculate the annualized return of a fund's price history
    ccr = float(calculate_cumulative_returns(prices))  # convert Decimal -> float
    num_years = (prices[-1][0] - prices[0][0]).days / 365.25
    annualized_return = (1 + ccr) ** (1 / num_years) - 1
    return annualized_return


def calculate_sharpe_ratio(prices, risk_free_rate=0.04): # calculate the Sharpe ratio of a fund's price history
    annualized_return = calculate_annualized_return(prices)
    annualized_volatility = calculate_volatility(calculate_daily_returns(prices))
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    return sharpe_ratio

# voo_prices = get_prices(3)
# print(calculate_annualized_return(voo_prices))
# print(calculate_sharpe_ratio(voo_prices))

def calculate_max_drawdown(prices): # calculate the maximum drawdown of a fund's price history
    max_drawdown = 0
    peak = prices[0][1]
    for date, price in prices:
        if price > peak:
            peak = price
        drawdown = (price - peak) / peak
        if drawdown < max_drawdown:
            max_drawdown = drawdown
    return max_drawdown

# voo_prices = get_prices(3)
# voo_max_dd = calculate_max_drawdown(voo_prices)
# print(voo_max_dd)

# ========================================================================================
import statistics

MIN_PRICES = 3   # stdev needs at least 2 daily returns, which needs 3 prices
RISK_FREE_RATE = 0.04   # assumption: flat 4% annual rate, not live market data


def _require_history(prices):
    if len(prices) < MIN_PRICES:
        raise ValueError(f"Need at least {MIN_PRICES} price rows, got {len(prices)}")

def calculate_daily_returns(prices): # calculate the daily returns of a fund's price history
    daily_returns = []
    for i in range(1, len(prices)):
        prev_close = float(prices[i - 1][1]) # close_price of the previous day
        curr_close = float(prices[i][1])     # close_price of the current day
        daily_return = (curr_close - prev_close) / prev_close
        daily_returns.append((prices[i][0], daily_return)) # append (date, daily_return)
    return daily_returns

def calculate_cumulative_returns(prices):
    _require_history(prices)
    early_price = float(prices[0][1]) # close_price of the first day
    latest_price = float(prices[-1][1]) # close_price of the last day
    return (latest_price - early_price) / early_price

def calculate_volatility(daily_returns): # calculate the annualized volatility of a fund's daily returns
    daily_return_values = [float(r[1]) for r in daily_returns] # extract the daily return values as floats
    daily_std_dev = statistics.stdev(daily_return_values) # calculate the standard deviation of daily returns
    volatility = daily_std_dev * (252 ** 0.5) # annualized volatility = standard deviation of daily returns * sqrt(252)
    return volatility

def calculate_annualized_return(prices): # calculate the annualized return of a fund's price history
    ccr = float(calculate_cumulative_returns(prices))  # convert Decimal -> float
    num_years = (prices[-1][0] - prices[0][0]).days / 365.25
    if num_years <= 0:
        raise ValueError("Price history spans zero days")
    annualized_return = (1 + ccr) ** (1 / num_years) - 1
    return annualized_return

def calculate_sharpe_ratio(prices, risk_free_rate=RISK_FREE_RATE):
    annualized_return = calculate_annualized_return(prices)
    annualized_volatility = calculate_volatility(calculate_daily_returns(prices))
    if annualized_volatility == 0:
        raise ValueError("Volatility is zero; Sharpe ratio is undefined")
    return (annualized_return - risk_free_rate) / annualized_volatility

def calculate_max_drawdown(prices):
    _require_history(prices)
    max_drawdown = 0.0
    peak = float(prices[0][1])
    for date, price in prices:
        price = float(price)
        if price > peak:
            peak = price
        drawdown = (price - peak) / peak
        if drawdown < max_drawdown:
            max_drawdown = drawdown
    return max_drawdown
import statistics

def calculate_daily_returns(prices): # calculate the daily returns of a fund's price history
    returns = []
    for i in range(1, len(prices)):
        prev_price = prices[i-1][1]  # close_price of previous day
        curr_price = prices[i][1]    # close_price of current day
        daily_return = (curr_price - prev_price) / prev_price
        returns.append((prices[i][0], daily_return))  # (date, daily_return)
    return returns

def calculate_cumulative_returns(prices): # calculate the cumulative return of a fund's price history
    early_price = prices[0][1]  # close_price of the first day
    latest_price = prices[-1][1]  # close_price of the last day
    cumulative_return = (latest_price - early_price) / early_price
    return cumulative_return

def calculate_volatility(daily_returns): # calculate the annualized volatility of a fund's daily returns
    daily_return_values = [float(r[1]) for r in daily_returns] # extract the daily return values as floats
    daily_std_dev = statistics.stdev(daily_return_values) # calculate the standard deviation of daily returns
    volatility = daily_std_dev * (252 ** 0.5) # annualized volatility = standard deviation of daily returns * sqrt(252)
    return volatility

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
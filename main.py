from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException
from db import get_funds, get_fund_id, get_prices
from analytics import (
    RISK_FREE_RATE,
    calculate_daily_returns,
    calculate_cumulative_returns,
    calculate_annualized_return,
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
)

app = FastAPI(title="FundSim API")


def load_history(ticker: str, start: Optional[date], end: Optional[date]):
    """Look up a fund and return its (date, close) rows within [start, end]."""
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="start must be on or before end")

    fund_id = get_fund_id(ticker.upper())
    if fund_id is None:
        raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker}")

    rows = get_prices(fund_id)
    return [
        (d, p) for d, p in rows
        if (start is None or d >= start) and (end is None or d <= end)
    ]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/funds")
def funds():
    rows = get_funds()
    return [
        {"ticker": ticker, "name": name,
         "expense_ratio": expense_ratio, "is_benchmark": is_benchmark}
        for ticker, name, expense_ratio, is_benchmark in rows
    ]


@app.get("/funds/{ticker}/prices")
def prices(ticker: str, start: Optional[date] = None, end: Optional[date] = None):
    rows = load_history(ticker, start, end)
    return [
        {"date": price_date.isoformat(), "close": float(close_price)}
        for price_date, close_price in rows
    ]


@app.get("/funds/{ticker}/metrics")
def metrics(ticker: str, start: Optional[date] = None, end: Optional[date] = None):
    rows = load_history(ticker, start, end)

    try:
        daily_returns = calculate_daily_returns(rows)
        cumulative_return = calculate_cumulative_returns(rows)
        annualized_return = calculate_annualized_return(rows)
        volatility = calculate_volatility(daily_returns)
        sharpe_ratio = calculate_sharpe_ratio(rows, risk_free_rate=RISK_FREE_RATE)
        max_drawdown = calculate_max_drawdown(rows)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "ticker": ticker.upper(),
        "period_start": rows[0][0].isoformat(),
        "period_end": rows[-1][0].isoformat(),
        "cumulative_return": cumulative_return,
        "annualized_return": annualized_return,
        "volatility": volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "risk_free_rate": RISK_FREE_RATE,
    }
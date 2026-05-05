from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

DEFAULT_TICKERS = [
    "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AMD","NFLX","UBER",
    "CRM","ORCL","ADBE","PYPL","SHOP","SPOT","PLTR","SQ","COIN","ARM",
    "ASML","TSM","BABA","JD","NIO","XPEV","SMCI","MU","QCOM","INTC",
    "JPM","GS","V","MA","BRK-B","BAC","WMT","COST","HD","LLY"
]

def compute_signal(ticker: str, period: str = "1y", fast: int = 20, slow: int = 50):
    try:
        data = yf.Ticker(ticker).history(period=period)
        if data.empty or len(data) < slow + 2:
            return None
        data['SMA_F'] = data['Close'].rolling(window=fast).mean()
        data['SMA_S'] = data['Close'].rolling(window=slow).mean()
        last_f = data['SMA_F'].iloc[-1]
        last_s = data['SMA_S'].iloc[-1]
        prev_f = data['SMA_F'].iloc[-2]
        prev_s = data['SMA_S'].iloc[-2]
        if last_f > last_s:
            verdict = "STRONG BUY" if prev_f <= prev_s else "HOLD"
        else:
            verdict = "STRONG SELL" if prev_f >= prev_s else "AVOID"
        price = round(float(data['Close'].iloc[-1]), 2)
        # 1-month change
        price_1m = float(data['Close'].iloc[-22]) if len(data) >= 22 else float(data['Close'].iloc[0])
        change_1m = round((price - price_1m) / price_1m * 100, 2)
        return {
            "ticker": ticker,
            "price": price,
            "change_1m": change_1m,
            "sma_fast": round(float(last_f), 2),
            "sma_slow": round(float(last_s), 2),
            "verdict": verdict
        }
    except:
        return None

@app.get("/api/analyze")
def analyze(ticker: str = "NVDA", period: str = "2y", fast: int = 20, slow: int = 50):
    data = yf.Ticker(ticker).history(period=period)
    if data.empty:
        return {"error": "No data found"}
    data['SMA_F'] = data['Close'].rolling(window=fast).mean()
    data['SMA_S'] = data['Close'].rolling(window=slow).mean()
    last_f, last_s = data['SMA_F'].iloc[-1], data['SMA_S'].iloc[-1]
    prev_f, prev_s = data['SMA_F'].iloc[-2], data['SMA_S'].iloc[-2]
    if last_f > last_s:
        verdict = "STRONG BUY" if prev_f <= prev_s else "HOLD"
    else:
        verdict = "STRONG SELL" if prev_f >= prev_s else "AVOID"
    chart_data = data[['Close', 'SMA_F', 'SMA_S']].dropna().tail(200)
    chart_data.index = chart_data.index.strftime('%Y-%m-%d')
    return {
        "verdict": verdict,
        "current_price": round(float(data['Close'].iloc[-1]), 2),
        "chart": chart_data.reset_index().rename(columns={"index": "Date"}).to_dict(orient="records")
    }

@app.get("/api/search")
def search(q: str = ""):
    if not q or len(q) < 2:
        return {"results": {"Nvidia (NVDA)": "NVDA"}}
    try:
        results = yf.Search(q, max_results=5).quotes
        return {"results": {f"{r.get('longname', r['symbol'])} ({r['symbol']})": r['symbol'] for r in results}}
    except:
        return {"results": {q.upper(): q.upper()}}

@app.get("/api/screener")
def screener(filter: str = "BUY"):
    """
    Scan DEFAULT_TICKERS and return those matching the filter.
    filter: BUY (HOLD + STRONG BUY), STRONG_BUY, SELL, ALL
    """
    results = []
    for t in DEFAULT_TICKERS:
        sig = compute_signal(t)
        if sig is None:
            continue
        v = sig["verdict"]
        if filter == "STRONG_BUY" and v != "STRONG BUY":
            continue
        elif filter == "BUY" and v not in ("BUY", "STRONG BUY", "HOLD"):
            continue
        elif filter == "SELL" and v not in ("SELL", "STRONG SELL", "AVOID"):
            continue
        results.append(sig)
    results.sort(key=lambda x: x["change_1m"], reverse=True)
    return {"results": results, "count": len(results)}

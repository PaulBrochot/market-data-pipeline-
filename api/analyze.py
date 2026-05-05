from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

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
    
    # Sérialiser les données pour le frontend
    chart_data = data[['Close', 'SMA_F', 'SMA_S']].dropna().tail(200)
    chart_data.index = chart_data.index.strftime('%Y-%m-%d')
    
    return {
        "verdict": verdict,
        "current_price": round(float(data['Close'].iloc[-1]), 2),
        "chart": chart_data.reset_index().rename(columns={"index": "date"}).to_dict(orient="records")
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
import yfinance as yf
import pandas as pd

# Liste des leaders technologiques (Magnificent Seven)
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
initial_capital = 10000.0
results_list = []

print(f"--- 🚀 MARKET SCANNER EN COURS (Analyse de {len(tickers)} actions) ---")

def backtest_scanner(ticker):
    # Ingestion des données
    data = yf.Ticker(ticker).history(period="2y")
    if len(data) < 150: return None
    
    # On utilise ici des paramètres stables (SMA 20 / SMA 50) pour comparer tout le monde équitablement
    fast_win, slow_win = 20, 50
    data['SMA_F'] = data['Close'].rolling(window=fast_win).mean()
    data['SMA_S'] = data['Close'].rolling(window=slow_win).mean()
    
    # Calcul du ROI historique
    cap, pos, in_pos = initial_capital, 0, False
    for i in range(slow_win, len(data)):
        if not in_pos and data['SMA_F'].iloc[i] > data['SMA_S'].iloc[i]:
            pos = cap / data['Close'].iloc[i]
            cap, in_pos = 0, True
        elif in_pos and data['SMA_F'].iloc[i] < data['SMA_S'].iloc[i]:
            cap = pos * data['Close'].iloc[i]
            pos, in_pos = 0, False
            
    final = cap if not in_pos else pos * data['Close'].iloc[-1]
    roi = ((final - initial_capital) / initial_capital) * 100
    
    # État actuel du marché
    last_fast = data['SMA_F'].iloc[-1]
    last_slow = data['SMA_S'].iloc[-1]
    current_signal = "🟢 ACHAT" if last_fast > last_slow else "🔴 VENTE"
    
    return {"Ticker": ticker, "ROI 2Y (%)": round(roi, 2), "Current Signal": current_signal}

# Exécution du scan
for t in tickers:
    print(f"Analyse de {t}...")
    res = backtest_scanner(t)
    if res: results_list.append(res)

# Affichage du tableau final
df_results = pd.DataFrame(results_list)
df_results = df_results.sort_values(by="ROI 2Y (%)", ascending=False)

print("\n" + "="*45)
print("          RÉSULTATS DU SCANNER             ")
print("="*45)
print(df_results.to_string(index=False))
print("="*45)
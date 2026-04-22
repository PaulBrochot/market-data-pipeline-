import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

ticker = "AAPL"
initial_capital = 10000.0

print(f"--- Optimisation & Visualisation pour {ticker} ---")

# 1. Récupération des données (2 ans)
data = yf.Ticker(ticker).history(period="2y")

# 2. Fonction de Backtesting (inchangée)
def run_backtest(sma_value, df):
    capital = initial_capital
    position = 0
    in_position = False
    df_temp = df.copy()
    df_temp['SMA'] = df_temp['Close'].rolling(window=sma_value).mean()
    for i in range(sma_value, len(df_temp)):
        price = df_temp.iloc[i]['Close']
        sma = df_temp.iloc[i]['SMA']
        prev_price = df_temp.iloc[i-1]['Close']
        prev_sma = df_temp.iloc[i-1]['SMA']
        if not in_position and price > sma and prev_price <= prev_sma:
            position = capital / price
            capital = 0
            in_position = True
        elif in_position and price < sma and prev_price >= prev_sma:
            capital = position * price
            position = 0
            in_position = False
    final_val = capital if not in_position else position * df_temp.iloc[-1]['Close']
    return ((final_val - initial_capital) / initial_capital) * 100

# 3. Boucle d'optimisation (en silencieux)
results = {}
for sma_test in range(10, 101, 5):
    results[sma_test] = run_backtest(sma_test, data)

best_sma = max(results, key=results.get)
print(f"Meilleure SMA trouvée : {best_sma} jours (Rendement : {results[best_sma]:.2f}%)")

# --- NOUVEAU : GÉNÉRATION DU GRAPHIQUE GAGNANT ---

print(f"Génération du graphique pour la SMA {best_sma}...")

# On recalcule les données pour la meilleure SMA
data['Best_SMA'] = data['Close'].rolling(window=best_sma).mean()

# Identification des points de signaux pour le graphique
data['Signal_Achat'] = None
data['Signal_Vente'] = None

for i in range(best_sma, len(data)):
    if data.iloc[i]['Close'] > data.iloc[i]['Best_SMA'] and data.iloc[i-1]['Close'] <= data.iloc[i-1]['Best_SMA']:
        data.at[data.index[i], 'Signal_Achat'] = data.iloc[i]['Close'] * 1.03
    elif data.iloc[i]['Close'] < data.iloc[i]['Best_SMA'] and data.iloc[i-1]['Close'] >= data.iloc[i-1]['Best_SMA']:
        data.at[data.index[i], 'Signal_Vente'] = data.iloc[i]['Close'] * 0.97

# Création du graphique
plt.figure(figsize=(14, 7))
plt.plot(data.index, data['Close'], label='Prix Réel (Close)', color='blue', alpha=0.5)
plt.plot(data.index, data['Best_SMA'], label=f'Meilleure SMA ({best_sma} jours)', color='orange', linestyle='--', linewidth=2)

# Ajout des triangles
plt.scatter(data.index, data['Signal_Achat'], label='Signal d\'Achat', marker='^', color='green', s=100, edgecolor='black')
plt.scatter(data.index, data['Signal_Vente'], label='Signal de Vente', marker='v', color='red', s=100, edgecolor='black')

plt.title(f"Stratégie Optimisée pour {ticker} (SMA {best_sma} | ROI {results[best_sma]:.2f}%)")
plt.xlabel("Date")
plt.ylabel("Prix (USD)")
plt.legend()
plt.grid(True, alpha=0.3)

# Affichage
plt.show()
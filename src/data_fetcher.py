import yfinance as yf
import pandas as pd

ticker = "AAPL"
initial_capital = 10000.0

print(f"--- Optimisation de la stratégie pour {ticker} ---")

# 1. Récupération des données
data = yf.Ticker(ticker).history(period="2y")

# 2. Fonction de Backtesting (pour pouvoir la tester en boucle)
def run_backtest(sma_value, df):
    capital = initial_capital
    position = 0
    in_position = False
    
    # Calcul de la SMA spécifique
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

# 3. BOUCLE D'OPTIMISATION : On teste de 10 à 100 jours
results = {}

print("Recherche de la meilleure SMA en cours...")
for sma_test in range(10, 101, 5): # Teste 10, 15, 20... jusqu'à 100
    performance = run_backtest(sma_test, data)
    results[sma_test] = performance
    print(f"Test SMA {sma_test} : {performance:.2f}%")

# 4. Affichage du gagnant
best_sma = max(results, key=results.get)
print("\n" + "="*40)
print(f"RÉSULTAT DE L'OPTIMISATION")
print(f"La meilleure SMA est : {best_sma} jours")
print(f"Rendement maximum    : {results[best_sma]:.2f}%")
print("="*40)
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="FinTech Market Scanner", layout="wide")

st.title("🚀 Market Scanner & Strategy Visualizer")
st.write("Analyse en temps réel des 'Magnificent Seven' avec stratégie Double SMA.")

# Configuration
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
initial_capital = 10000.0

@st.cache_data(ttl=3600) # Pour ne pas retélécharger les données à chaque clic
def get_data(symbol):
    return yf.Ticker(symbol).history(period="2y")

# --- PARTIE 1 : LE TABLEAU DE BORD ---
st.header("📊 Market Overview")
results = []

for t in tickers:
    df = get_data(t)
    # Paramètres optimisés par défaut (20/50)
    df['SMA_F'] = df['Close'].rolling(window=20).mean()
    df['SMA_S'] = df['Close'].rolling(window=50).mean()
    
    # Calcul rapide du ROI
    # (Logique simplifiée pour le tableau)
    last_fast = df['SMA_F'].iloc[-1]
    last_slow = df['SMA_S'].iloc[-1]
    signal = "🟢 BUY" if last_fast > last_slow else "🔴 SELL"
    
    # Performance simplifiée (Prix actuel vs Prix il y a 1 an)
    perf = ((df['Close'].iloc[-1] - df['Close'].iloc[-252]) / df['Close'].iloc[-252]) * 100
    results.append({"Ticker": t, "1Y Performance (%)": round(perf, 2), "Current Signal": signal})

df_res = pd.DataFrame(results)
st.table(df_res) # Affiche un tableau propre

# --- PARTIE 2 : ANALYSE DÉTAILLÉE ---
st.header("🔍 Deep Dive Analysis")
selected_ticker = st.selectbox("Sélectionne une action pour voir les signaux détaillés :", tickers)

if selected_ticker:
    data = get_data(selected_ticker)
    f_win, s_win = 20, 50 # On peut ajouter des curseurs ici plus tard
    
    data['SMA_F'] = data['Close'].rolling(window=f_win).mean()
    data['SMA_S'] = data['Close'].rolling(window=s_win).mean()
    
    # Identification des signaux pour les triangles
    data['Buy_Sig'] = (data['SMA_F'] > data['SMA_S']) & (data['SMA_F'].shift(1) <= data['SMA_S'].shift(1))
    data['Sell_Sig'] = (data['SMA_F'] < data['SMA_S']) & (data['SMA_F'].shift(1) >= data['SMA_S'].shift(1))

    # Création du graphique Matplotlib
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data.index, data['Close'], label='Price', color='black', alpha=0.2)
    ax.plot(data.index, data['SMA_F'], label=f'Fast SMA ({f_win})', color='#2ecc71')
    ax.plot(data.index, data['SMA_S'], label=f'Slow SMA ({s_win})', color='#e74c3c')
    
    # Ajout des triangles
    ax.plot(data[data['Buy_Sig']].index, data['SMA_F'][data['Buy_Sig']], '^', markersize=10, color='g', label='Buy Signal')
    ax.plot(data[data['Sell_Sig']].index, data['SMA_F'][data['Sell_Sig']], 'v', markersize=10, color='r', label='Sell Signal')
    
    ax.set_title(f"Analyse Technique détaillée pour {selected_ticker}")
    ax.legend()
    st.pyplot(fig) # Affiche le graphique dans l'interface web
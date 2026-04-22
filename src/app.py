import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="QuantScanner AI", layout="wide")

# --- BARRE LATÉRALE ---
st.sidebar.header("⚙️ Paramètres")
user_ticker = st.sidebar.text_input("Ticker", "AAPL").upper()
period = st.sidebar.selectbox("Période", ["1y", "2y", "5y"], index=1)

# Initialisation des valeurs par défaut dans la "session_state"
if 'fast_ma' not in st.session_state: st.session_state.fast_ma = 20
if 'slow_ma' not in st.session_state: st.session_state.slow_ma = 50

# --- LOGIQUE D'OPTIMISATION ---
def run_backtest(f_win, s_win, df):
    if f_win >= s_win: return -100
    d = df.copy()
    d['F'] = d['Close'].rolling(window=f_win).mean()
    d['S'] = d['Close'].rolling(window=s_win).mean()
    cap, pos, in_pos = 10000.0, 0, False
    for i in range(s_win, len(d)):
        if not in_pos and d['F'].iloc[i] > d['S'].iloc[i]:
            pos = cap / d['Close'].iloc[i]
            cap, in_pos = 0, True
        elif in_pos and d['F'].iloc[i] < d['S'].iloc[i]:
            cap = pos * d['Close'].iloc[i]
            pos, in_pos = 0, False
    final = cap if not in_pos else pos * d['Close'].iloc[-1]
    return ((final - 10000.0) / 10000.0) * 100

data = yf.Ticker(user_ticker).history(period=period)

if st.sidebar.button("🚀 Optimiser la stratégie"):
    with st.sidebar:
        progress_bar = st.progress(0)
        best_roi, best_f, best_s = -100, 0, 0
        tests = [(f, s) for f in range(5, 31, 5) for s in range(40, 151, 10)]
        
        for i, (f, s) in enumerate(tests):
            roi = run_backtest(f, s, data)
            if roi > best_roi:
                best_roi, best_f, best_s = roi, f, s
            progress_bar.progress((i + 1) / len(tests))
        
        st.session_state.fast_ma = best_f
        st.session_state.slow_ma = best_s
        st.success(f"Optimisé ! Meilleur ROI: {best_roi:.2f}%")

# Sliders liés à la session_state
fast_ma = st.sidebar.slider("Moyenne Courte", 5, 50, st.session_state.fast_ma)
slow_ma = st.sidebar.slider("Moyenne Longue", 40, 200, st.session_state.slow_ma)

# --- AFFICHAGE PRINCIPAL ---
st.title(f"📈 Analyse Stratégique : {user_ticker}")

if not data.empty:
    data['SMA_F'] = data['Close'].rolling(window=fast_ma).mean()
    data['SMA_S'] = data['Close'].rolling(window=slow_ma).mean()
    data['Buy_Sig'] = (data['SMA_F'] > data['SMA_S']) & (data['SMA_F'].shift(1) <= data['SMA_S'].shift(1))
    data['Sell_Sig'] = (data['SMA_F'] < data['SMA_S']) & (data['SMA_F'].shift(1) >= data['SMA_S'].shift(1))

    c1, c2, c3 = st.columns(3)
    c1.metric("Prix Actuel", f"{data['Close'].iloc[-1]:.2f} $")
    c2.metric("Configuration", f"{fast_ma} / {slow_ma}")
    
    current_roi = run_backtest(fast_ma, slow_ma, data)
    c3.metric("ROI Stratégie", f"{current_roi:.2f} %")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(data.index, data['Close'], label='Prix', color='black', alpha=0.1)
    ax.plot(data.index, data['SMA_F'], label=f'Fast {fast_ma}', color='#2ecc71', lw=2)
    ax.plot(data.index, data['SMA_S'], label=f'Slow {slow_ma}', color='#e74c3c', lw=2)
    ax.plot(data[data['Buy_Sig']].index, data['SMA_F'][data['Buy_Sig']], '^', markersize=12, color='g', label='ACHAT')
    ax.plot(data[data['Sell_Sig']].index, data['SMA_F'][data['Sell_Sig']], 'v', markersize=12, color='r', label='VENTE')
    ax.set_title(f"Signaux de Trading pour {user_ticker}")
    ax.legend()
    st.pyplot(fig)

    # --- SECTION DONNÉES BRUTES ---
st.divider() # Ajoute une ligne de séparation propre
st.header("📋 Données Historiques & Signaux")

# On crée deux onglets : un pour les 10 dernières lignes, un pour tout voir
tab1, tab2 = st.tabs(["Dernières séances", "Historique complet"])

with tab1:
    st.write("Voici les 10 derniers jours de bourse avec les calculs de moyennes :")
    # On affiche les 10 dernières lignes, en inversant pour voir le plus récent en haut
    st.dataframe(data.tail(10).sort_index(ascending=False))

with tab2:
    st.write("Télécharger ou explorer l'intégralité des données :")
    st.dataframe(data)
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="QuantScanner AI - Pro Dashboard", layout="wide")

# --- SMART SEARCH LOGIC (FONCTION DE RECHERCHE) ---
@st.cache_data(ttl=3600)
def get_ticker_suggestions(query):
    if not query or len(query) < 2:
        return {"Nvidia (NVDA)": "NVDA"}
    try:
        search = yf.Search(query, max_results=5)
        if search.quotes:
            return {f"{r.get('longname', r['symbol'])} ({r['symbol']})": r['symbol'] for r in search.quotes}
        return {f"{query.upper()}": query.upper()}
    except:
        return {f"{query.upper()}": query.upper()}

# --- BARRE LATÉRALE (SIDEBAR) ---
st.sidebar.header("🔍 Search & Settings")

# Moteur de recherche universel (Vide par défaut)
search_query = st.sidebar.text_input("Type Company Name", value="", placeholder="Ex: Nvidia, LVMH, Bitcoin...")

# Arrêt de l'application si aucune recherche n'est faite
if not search_query:
    st.title("📈 Welcome to QuantScanner AI")
    st.info("👋 Please enter a company name or ticker in the sidebar to start your analysis.")
    st.stop()

suggestions = get_ticker_suggestions(search_query)
selected_display = st.sidebar.selectbox("Select Result", options=list(suggestions.keys()))
user_ticker = suggestions[selected_display]

period = st.sidebar.selectbox("Historical Period", ["1y", "2y", "5y"], index=1)

# Initialisation de la mémoire (Session State)
if 'fast_ma' not in st.session_state: st.session_state.fast_ma = 20
if 'slow_ma' not in st.session_state: st.session_state.slow_ma = 50

# --- LOGIQUE DE BACKTESTING ---
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

# --- CHARGEMENT DES DONNÉES AVEC CACHE (5 min) ---
@st.cache_data(ttl=300)
def load_data(ticker, period):
    return yf.Ticker(ticker).history(period=period)

# --- PRIX LIVE VIA FAST_INFO ---
def get_live_price(ticker):
    try:
        return round(float(yf.Ticker(ticker).fast_info["last_price"]), 2)
    except:
        return None

data = load_data(user_ticker, period)

# --- MOTEUR D'OPTIMISATION ---
if st.sidebar.button("🚀 Optimize Strategy"):
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
        st.success(f"Optimized! ROI: {best_roi:.2f}%")

# Sliders
fast_ma = st.sidebar.slider("Fast SMA (Short Term)", 5, 50, st.session_state.fast_ma)
slow_ma = st.sidebar.slider("Slow SMA (Long Term)", 40, 200, st.session_state.slow_ma)

# --- DASHBOARD PRINCIPAL ---
st.title(f"📈 Analysis: {selected_display}")

if not data.empty:
    # Calculs techniques
    data['SMA_F'] = data['Close'].rolling(window=fast_ma).mean()
    data['SMA_S'] = data['Close'].rolling(window=slow_ma).mean()
    data['Buy_Sig'] = (data['SMA_F'] > data['SMA_S']) & (data['SMA_F'].shift(1) <= data['SMA_S'].shift(1))
    data['Sell_Sig'] = (data['SMA_F'] < data['SMA_S']) & (data['SMA_F'].shift(1) >= data['SMA_S'].shift(1))

    # --- SECTION VERDICT ---
    last_f, last_s = data['SMA_F'].iloc[-1], data['SMA_S'].iloc[-1]
    prev_f, prev_s = data['SMA_F'].iloc[-2], data['SMA_S'].iloc[-2]

    if last_f > last_s:
        v_text, v_desc, v_col = ("🚀 STRONG BUY", "Bullish crossover!", "#27ae60") if prev_f <= prev_s else ("📈 HOLD", "Trend is still bullish.", "#2980b9")
    else:
        v_text, v_desc, v_col = ("⚠️ STRONG SELL", "Bearish crossover!", "#c0392b") if prev_f >= prev_s else ("💤 AVOID / CASH", "Market is bearish.", "#7f8c8d")

    st.markdown(f"""<div style="padding:20px; border-radius:10px; background-color:{v_col}; color:white; text-align:center; margin-bottom:25px;">
        <h1 style="margin:0;">{v_text}</h1><p style="margin:0; font-size:1.2em;">{v_desc}</p></div>""", unsafe_allow_html=True)

    # Métriques — prix live via fast_info
    live_price = get_live_price(user_ticker)
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Price", f"{live_price if live_price else data['Close'].iloc[-1]:.2f} $")
    c2.metric("SMA Config", f"{fast_ma} / {slow_ma}")
    c3.metric("Strategy ROI", f"{run_backtest(fast_ma, slow_ma, data):.2f} %")

    # Graphique
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(data.index, data['Close'], label='Price', color='black', alpha=0.1)
    ax.plot(data.index, data['SMA_F'], label=f'Fast ({fast_ma})', color='#2ecc71', lw=2)
    ax.plot(data.index, data['SMA_S'], label=f'Slow ({slow_ma})', color='#e74c3c', lw=2)
    ax.plot(data[data['Buy_Sig']].index, data['SMA_F'][data['Buy_Sig']], '^', markersize=12, color='g', label='BUY')
    ax.plot(data[data['Sell_Sig']].index, data['SMA_F'][data['Sell_Sig']], 'v', markersize=12, color='r', label='SELL')
    ax.legend()
    st.pyplot(fig)

    # Données brutes
    st.divider()
    t1, t2 = st.tabs(["Recent Data", "Full History"])
    with t1: st.dataframe(data.tail(10).sort_index(ascending=False))
    with t2: st.dataframe(data)
else:
    st.warning("No data found. Please check your search.")

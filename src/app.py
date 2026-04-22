import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(page_title="QuantScanner AI - Pro Dashboard", layout="wide")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Strategy Settings")
user_ticker = st.sidebar.text_input("Ticker Symbol", "AAPL").upper()
period = st.sidebar.selectbox("Historical Period", ["1y", "2y", "5y"], index=1)

# Initialize Session State for persistence
if 'fast_ma' not in st.session_state: st.session_state.fast_ma = 20
if 'slow_ma' not in st.session_state: st.session_state.slow_ma = 50

# --- BACKTESTING LOGIC ---
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

# Data Fetching
@st.cache_data(ttl=3600)  # Garde les données en mémoire pendant 1h
def load_data(ticker, period):
    return yf.Ticker(ticker).history(period=period)

data = load_data(user_ticker, period)

# --- OPTIMIZATION ENGINE ---
if st.sidebar.button("🚀 Optimize Strategy"):
    with st.sidebar:
        progress_bar = st.progress(0)
        best_roi, best_f, best_s = -100, 0, 0
        # Grid Search across parameters
        tests = [(f, s) for f in range(5, 31, 5) for s in range(40, 151, 10)]
        
        for i, (f, s) in enumerate(tests):
            roi = run_backtest(f, s, data)
            if roi > best_roi:
                best_roi, best_f, best_s = roi, f, s
            progress_bar.progress((i + 1) / len(tests))
        
        # Update session state with best parameters
        st.session_state.fast_ma = best_f
        st.session_state.slow_ma = best_s
        st.success(f"Optimization Complete! Best ROI: {best_roi:.2f}%")

# Sliders linked to session state
fast_ma = st.sidebar.slider("Fast SMA (Sensitivity)", 5, 50, st.session_state.fast_ma)
slow_ma = st.sidebar.slider("Slow SMA (Trend)", 40, 200, st.session_state.slow_ma)

# --- MAIN DASHBOARD ---
st.title(f"📈 Strategic Analysis: {user_ticker}")

if not data.empty:
    # Calculations
    data['SMA_F'] = data['Close'].rolling(window=fast_ma).mean()
    data['SMA_S'] = data['Close'].rolling(window=slow_ma).mean()
    data['Buy_Sig'] = (data['SMA_F'] > data['SMA_S']) & (data['SMA_F'].shift(1) <= data['SMA_S'].shift(1))
    data['Sell_Sig'] = (data['SMA_F'] < data['SMA_S']) & (data['SMA_F'].shift(1) >= data['SMA_S'].shift(1))

    # --- CURRENT VERDICT SECTION ---
    last_f = data['SMA_F'].iloc[-1]
    last_s = data['SMA_S'].iloc[-1]
    prev_f = data['SMA_F'].iloc[-2]
    prev_s = data['SMA_S'].iloc[-2]

    if last_f > last_s:
        if prev_f <= prev_s:
            v_text, v_desc, v_col = "🚀 STRONG BUY", "New bullish crossover detected today! High momentum.", "#27ae60"
        else:
            v_text, v_desc, v_col = "📈 HOLD", "Bullish trend confirmed. Maintain current positions.", "#2980b9"
    else:
        if prev_f >= prev_s:
            v_text, v_desc, v_col = "⚠️ STRONG SELL", "Bearish crossover detected. Exit positions immediately.", "#c0392b"
        else:
            v_text, v_desc, v_col = "💤 AVOID / CASH", "Market is bearish or neutral. Stay out of the market.", "#7f8c8d"

    st.markdown(f"""
        <div style="padding:20px; border-radius:10px; background-color:{v_col}; color:white; text-align:center; margin-bottom:25px;">
            <h1 style="margin:0; font-size:2.5em;">{v_text}</h1>
            <p style="margin:0; font-size:1.3em; opacity:0.9;">{v_desc}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- KEY METRICS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Price", f"{data['Close'].iloc[-1]:.2f} $")
    c2.metric("Configuration (F/S)", f"{fast_ma} / {slow_ma}")
    current_roi = run_backtest(fast_ma, slow_ma, data)
    c3.metric("Strategy ROI", f"{current_roi:.2f} %")

    # --- CHARTING ---
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(data.index, data['Close'], label='Asset Price', color='black', alpha=0.1)
    ax.plot(data.index, data['SMA_F'], label=f'Fast SMA ({fast_ma})', color='#2ecc71', lw=2)
    ax.plot(data.index, data['SMA_S'], label=f'Slow SMA ({slow_ma})', color='#e74c3c', lw=2)
    
    # Signals
    ax.plot(data[data['Buy_Sig']].index, data['SMA_F'][data['Buy_Sig']], '^', markersize=12, color='g', label='BUY Signal')
    ax.plot(data[data['Sell_Sig']].index, data['SMA_F'][data['Sell_Sig']], 'v', markersize=12, color='r', label='SELL Signal')
    
    ax.set_title(f"Technical Analysis for {user_ticker}")
    ax.legend(loc='best')
    st.pyplot(fig)

    # --- RAW DATA SECTION ---
    st.divider()
    st.header("📋 Data Audit & Signal Log")
    tab1, tab2 = st.tabs(["Recent Sessions", "Full Dataset"])

    with tab1:
        st.write("Detailed calculations for the last 10 trading sessions:")
        st.dataframe(data.tail(10).sort_index(ascending=False))

    with tab2:
        st.write("Full historical dataset exploration:")
        st.dataframe(data)
else:
    st.warning("No data found. Please check the Ticker symbol.")
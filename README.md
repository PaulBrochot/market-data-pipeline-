# 📈 QuantScanner AI : Algorithmic Trading & Strategy Optimizer

🚀 **[Live Demo: Access the QuantScanner AI App](https://paul-quant-scanner.streamlit.app)**

A professional Python-based quantitative analysis tool designed for financial data ingestion, algorithmic strategy backtesting, and parameter optimization. 

Built as a technical proof-of-concept for **FinTech** and **Data Engineering** internships.

## 🚀 Key Features

* **Universal Asset Search:** Integrated auto-suggest engine to find any stock, crypto, or forex pair by company name (no need to remember tickers).
* **AI Optimization Engine:** Features a Grid Search optimization script that tests dozens of SMA combinations to identify the mathematically optimal strategy for any given asset.
* **Algorithmic Strategy:** Implements a Trend-Following strategy based on Dual Simple Moving Average (SMA) crossovers.
* **Real-Time Data Pipeline:** Automated ingestion of live market data using the `yfinance` API with built-in **caching** for high performance.
* **Data Visualization:** Actionable charting with `matplotlib` showing price action, moving averages, and precise Buy/Sell signals.

## 🛠️ Tech Stack

* **Language:** Python 3.12+
* **Framework:** Streamlit (Web UI & Deployment)
* **Data Science:** Pandas, NumPy
* **Financial API:** yfinance
* **Visualization:** Matplotlib

## 📊 Performance Results (Example: NVDA)
Through automated optimization, the strategy performance was significantly enhanced:
* **Standard SMA Configuration:** ~12.40% ROI
* **Optimized Configuration:** **+51.95% ROI** (based on 2-year backtest)
* *Note: This demonstrates the power of data-driven parameter tuning in algorithmic trading.*

## 💻 Installation & Quick Start

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/PaulBrochot/market-data-pipeline-.git](https://github.com/PaulBrochot/market-data-pipeline-.git)
   cd market-data-pipeline-
   pip install -r requirements.txt
   streamlit run src/app.py

## 🗺️ Roadmap & Future Improvements
You can track the ongoing development and upcoming features in the Projects tab.

[ ] RSI Integration: Adding momentum filters to refine entry points.

[ ] Reporting Engine: Exporting backtest results to PDF/Excel reports.

[ ] Risk Management: Implementing automated Stop-Loss and Take-Profit calculations.

Created by Paul Brochot - Engineering Student



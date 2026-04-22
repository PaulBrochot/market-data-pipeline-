# 📈 Market Data Pipeline & Strategy Optimizer

A professional Python-based quantitative analysis tool designed for financial data ingestion, algorithmic strategy backtesting, and parameter optimization. 

Built as a technical proof-of-concept for **FinTech** and **Data Engineering** internships.

## 🚀 Key Features

* **Real-Time Data Pipeline:** Automated ingestion of historical and live market data using the `yfinance` API.
* **Algorithmic Strategy:** Implements a Trend-Following strategy based on Simple Moving Average (SMA) crossovers.
* **Backtesting Engine:** Simulates trading performance over a 2-year historical period to calculate ROI and total returns.
* **Parameter Optimization:** Features a brute-force optimization script that tests multiple SMA windows (from 10 to 100 days) to identify the mathematically optimal strategy for any given asset.
* **Data Visualization:** Clear, actionable charting with `matplotlib` showing price action, moving averages, and precise entry/exit signals.

## 🛠️ Tech Stack

* **Language:** Python 3.12+
* **Data Science:** Pandas, NumPy
* **Financial API:** yfinance
* **Visualization:** Matplotlib

## 📊 Performance Results (Example: AAPL)
Through automated optimization, the strategy performance was significantly enhanced:
* **Standard SMA-20 ROI:** ~5.40%
* **Optimized SMA-10 ROI:** **33.36%**
* *Note: This demonstrates the power of data-driven parameter tuning in algorithmic trading.*

## 💻 Installation & Quick Start

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/PaulBrochot/market-data-pipeline-.git](https://github.com/PaulBrochot/market-data-pipeline-.git)
   cd market-data-pipeline-
import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import datetime

# ===== 1. ETF 종목 및 비중 설정 =====
tickers = {
    "498400": 0.30,  # KODEX 200 타겟위클리커버드콜
    "475720": 0.30,  # KB RISE 200 위클리커버드콜
    "148020": 0.30   # KB RISE 200
}
cash_weight = 0.10

# ===== 2. 기간 설정 =====
start = "2024-12-01"
end = "2025-09-06"

# ===== 3. 데이터 다운로드 (FDR 사용) =====
data = pd.DataFrame()
for t in tickers.keys():
    df = fdr.DataReader(t, start, end)
    data[t] = df["Close"]

# ===== 4. 수익률 및 누적 가치 계산 =====
rets = data.pct_change().fillna(0)
portfolio_ret = sum(rets[t] * w for t, w in tickers.items())
portfolio_ret = portfolio_ret * (1 - cash_weight)

port_value = (1 + portfolio_ret).cumprod() * 100
etf_values = (1 + rets).cumprod() * 100

# ===== 5. CAGR & MDD =====
years = (port_value.index[-1] - port_value.index[0]).days / 365.25
cagr = (port_value.iloc[-1] / port_value.iloc[0]) ** (1/years) - 1

cum_max = port_value.cummax()
drawdown = (port_value - cum_max) / cum_max
mdd = drawdown.min()

# ===== 6. 결과 출력 =====
print(f"백테스트 기간: {start} ~ {end}")
print(f"포트폴리오 CAGR: {cagr:.2%}")
print(f"포트폴리오 MDD : {mdd:.2%}")

# ===== 7. 그래프 =====
plt.figure(figsize=(12,6))
plt.plot(port_value, label="Portfolio", color="black", linewidth=2)
for t in tickers.keys():
    plt.plot(etf_values[t], label=t)
plt.legend()
plt.title("Portfolio vs ETFs")
plt.show()

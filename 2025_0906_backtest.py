import pandas as pd
import FinanceDataReader as fdr
import numpy as np

# ETF 종목 및 비중 설정
tickers = {
    "498400": 0.30,
    "475720": 0.30,
    "148020": 0.30
}

start = "2024-12-03"
end = "2025-09-06"
commission_rate = 0.00015  # 0.015%

# 데이터 다운로드
data = pd.DataFrame()
for t in tickers.keys():
    df = fdr.DataReader(t, start, end)
    data[t] = df["Close"]

# 일별 수익률 계산
rets = data.pct_change().fillna(0)

# 포트폴리오 목표 비중 DataFrame 생성 (매일 동일 비중 유지 가정)
weights = pd.DataFrame(index=rets.index, columns=tickers.keys())
for t in tickers.keys():
    weights[t] = tickers[t]

# 리밸런싱 날짜를 매월 첫 거래일로 설정
rebalance_dates = weights.resample('MS').first().index  # 월별 첫 날짜(영업일 기준)

# 수수료 차감 적용한 수익률 계산용 빈 시리즈 생성
net_portfolio_ret = pd.Series(0, index=rets.index)

# 초기 비중 설정
prev_weights = pd.Series(0, index=tickers.keys())

for date in rets.index:
    # 리밸런싱일인 경우 거래 발생
    if date in rebalance_dates:
        new_weights = weights.loc[date]
        # 비중 변화량의 절대합 ~= 거래 비율
        trade_volume = (new_weights - prev_weights).abs().sum()
        # 수수료 차감율
        commission_fee = trade_volume * commission_rate
        prev_weights = new_weights
    else:
        commission_fee = 0  # 리밸런싱 아닌 날은 수수료 없음

    # 해당일 포트폴리오 수익률 (비중별 가중 합)
    daily_ret = (rets.loc[date] * prev_weights).sum()

    # 수수료 차감
    net_portfolio_ret.loc[date] = daily_ret - commission_fee

# 누적 수익률, 누적 가치 계산
port_value = (1 + net_portfolio_ret).cumprod() * 100
etf_values = (1 + rets).cumprod() * 100

# 기간 계산 (영업일 기준)
trading_days = len(port_value) - 1
years = trading_days / 252

# CAGR, MDD 계산
cagr = (port_value.iloc[-1] / port_value.iloc[0]) ** (1/years) - 1
cum_max = port_value.cummax()
drawdown = (port_value - cum_max) / cum_max
mdd = drawdown.min()

# 결과 출력
print(f"백테스트 기간: {start} ~ {end}")
print(f"수수료율: {commission_rate*100:.3f}% 반영")
print(f"포트폴리오 CAGR (수수료 차감): {cagr:.2%}")
print(f"포트폴리오 MDD : {mdd:.2%}")

import yfinance as yf
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # 设置 Matplotlib 后端为 TkAgg
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd
from ib_insync import Stock, IB

# 获取股票数据
# stock = yf.Ticker("ETNB")
# # stock = yf.Ticker("UBER")
# # stock = yf.Ticker("META")
# # data = stock.history(period="3mo", interval="1d")
# data = stock.history(period="3mo", interval="1d")

ib = IB()
ib.connect('104.194.79.173', 4001, clientId=1, timeout=30)  # 7497 是纸交易端口，7496 是真实交易端口

# symbol = "ETNB"
# symbol = "ACMR"
symbol = "NLY"
# 定义 AAPL 股票合约
contract = Stock(f"{symbol}", 'SMART', 'USD')

# 设置查询结束时间（使用 UTC 格式，避免时区错误）
end_time = '20250215-00:00:00'  # 2025年2月8日 00:00:00 UTC

# 请求历史数据
bars = ib.reqHistoricalData(
    contract,
    endDateTime=end_time,  # 修正格式
    durationStr='90 D',  # 查询过去 2 天数据
    barSizeSetting='1 day',  # 按日获取数据
    whatToShow='TRADES',  # 交易数据
    useRTH=True,  # 仅使用正常交易时间的数据
    formatDate=1
)

# print(bars)

# 将 BarData 转换为 DataFrame
data = pd.DataFrame([{
    "date": bar.date,
    "open": bar.open,
    "high": bar.high,
    "low": bar.low,
    "Close": bar.close,
    "Volume": bar.volume,
    "average": bar.average,
    "barCount": bar.barCount
} for bar in bars])

if data.empty:
    print(f"No data found for {symbol}. Skipping...")
    exit()

# 将 date 列转换为索引
data.set_index('date', inplace=True)


data["code"] = symbol  # 添加 code 列
print(data)

# 清理数据，移除NaN或Inf值
data = data.dropna()
data = data[np.isfinite(data['Close'])]

# 计算SMA（简单移动平均）
data['SMA50'] = data['Close'].rolling(window=50).mean()

# print(data)

# 识别杯柄形态
def bowl(x, a, b, c):
    """开口朝上的二次曲线拟合函数，用于识别杯形底部"""
    return -a * (x - b)**2 + c  # 修改为负数的抛物线，杯口朝上

def find_bowl(data, fit_window=20):
    """通过曲线拟合来寻找杯形底部"""
    x = np.arange(len(data))
    y = data['Close'].values

    # 选择拟合的范围
    #fit_data = data.iloc[-60:]  # 只用最后60天的数据
    fit_data = data.iloc[-fit_window:]  # 只用最后180天的数据
    x_fit = np.arange(len(fit_data))
    y_fit = fit_data['Close'].values

    # 曲线拟合
    popt, _ = curve_fit(bowl, x_fit, y_fit, p0=[0.001, len(fit_data)//2, min(y_fit)])

    return popt, fit_data

# 获取杯形底部的拟合参数
# params, fit_data = find_bowl(data)

# 绘制股价和拟合的曲线
# plt.figure(figsize=(10, 6))
# plt.plot(data['Close'], label='Close Price')
# plt.plot(fit_data.index, bowl(np.arange(len(fit_data)), *params), label='Fitted Bowl', linestyle='--')
# plt.title('META Stock Price with Cup and Handle Pattern (Fitted) - Bowl Opening Upwards')
# plt.xlabel('Date')
# plt.ylabel('Price')
# plt.legend()
# plt.show()

# 识别杯柄形态的突破点
def identify_cup_handle_breakout(data, cup_up=0.015, cup_depth_threshold=0.06, handle_depth_threshold=0.08, volume_threshold=1.1, min_cup_days=13, min_dur_day = 9):
    """
    识别杯柄形态的突破点，自动确定杯子的开始和结束日期。
    :param data: 股票数据
    :param cup_depth_threshold: 杯子深度的阈值（百分比）
    :param handle_depth_threshold: 柄部深度的阈值（百分比）
    :param volume_threshold: 成交量放大倍数
    :param min_cup_days: 杯子至少要有多少个交易日的长度
    :return: 突破点的日期列表
    """
    breakout_points = []

    # 遍历整个数据寻找多个杯柄形态
    i = 0
    while i < len(data):
        # 寻找杯子的起始点
        cup_start = None
        cup_start_price = None
        cup_end = None
        cup_end_price = None
        cup_min = None

        # 遍历数据查找杯子的开始
        for j in range(i, len(data)):
            if j > 0 and data['Close'].iloc[j] < data['Close'].iloc[j-1]:
                # 如果股价开始下跌，记录杯子的开始
                if cup_start is None:
                    cup_start = data.index[j-1]
                    cup_start_price = data['Close'].iloc[j-1]
                cup_min = min(cup_min, data['Close'].iloc[j]) if cup_min is not None else data['Close'].iloc[j]
            elif (cup_start is not None
                  and (data['Close'].iloc[j]) * (1 + cup_up) > data['Close'].iloc[j-1]
                  and (cup_start_price * (1 - cup_up) <= data['Close'].iloc[j] or cup_start_price <= data['Close'].iloc[j] <= cup_start_price * (1 + cup_up))):
                # 如果股价开始上升，认为杯子的结束部分找到了
                cup_end = data.index[j]
                cup_end_price = data['Close'].iloc[j]
                break

        print(f"cup_start: {cup_start}")
        print(f"cup_start_price: {cup_start_price}")
        print(f"cup_min: {cup_min}")
        print(f"cup_end: {cup_end}")
        print(f"cup_end_price: {cup_end_price}")

        # 如果杯子的深度符合要求且持续时间足够
        if cup_start is not None and cup_end is not None:
            # 检查杯子深度是否满足阈值
            cup_depth = (data.loc[cup_start, 'Close'] - cup_min) / data.loc[cup_start, 'Close']
            cup_duration = (data.index.get_loc(cup_end) - data.index.get_loc(cup_start))
            if cup_depth >= cup_depth_threshold and cup_duration >= min_cup_days:
                # 寻找柄部
                handle_start = cup_end
                handle_end = None
                handle_min = None
                for j in range(data.index.get_loc(handle_start), len(data)):
                    if data['Close'].iloc[j] < data['Close'].iloc[j-1]:
                        handle_min = min(handle_min, data['Close'].iloc[j]) if handle_min is not None else data['Close'].iloc[j]
                    elif handle_min is not None:
                        handle_end = data.index[j]
                        break

                # 检查柄部深度是否满足阈值
                if handle_start is not None and handle_end is not None:
                    handle_depth = (data.loc[handle_start, 'Close'] - handle_min) / data.loc[handle_start, 'Close']
                    if handle_depth <= handle_depth_threshold:

                        # 设置一个窗口，检查handle_end前后3天的数据
                        handle_end_loc = data.index.get_loc(handle_end)
                        start_range = max(handle_end_loc - min_dur_day, 0)  # 确保不超出数据的开始
                        end_range = min(handle_end_loc + min_dur_day, len(data) - 1)  # 确保不超出数据的结尾

                        # 寻找突破点
                        print(f"handle_end :{handle_end}")
                        for j in range(start_range, end_range + 1):
                            if (data['Close'].iloc[j] > data.loc[handle_start, 'Close']
                                    and data['Volume'].iloc[j] > volume_threshold * data['Volume'].iloc[j-1]
                                    and handle_end is not None):
                                breakout_points.append(data.index[j])
                # 更新扫描的位置，跳到下一个可能的杯形底部
                i = data.index.get_loc(cup_end) + 1
            else:
                i = data.index.get_loc(cup_end) + 1
        else:
            break  # 如果没有找到更多的杯子，结束循环

    return breakout_points

# 识别突破点
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', 1000)        # 设置显示宽度
print(data)
breakout_points = identify_cup_handle_breakout(data)
print(breakout_points)

# 绘制股价图表和突破点
plt.figure(figsize=(10, 6))
plt.plot(data['Close'], label='Close Price')
if breakout_points:
    plt.scatter(breakout_points, data.loc[breakout_points]['Close'], color='red', label='Breakout Points')
plt.title(f'{symbol} Stock Price with Cup and Handle Breakout Points')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

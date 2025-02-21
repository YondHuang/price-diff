import yfinance as yf
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # 设置 Matplotlib 后端为 TkAgg
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 获取股票数据
stock = yf.Ticker("MSFT")
data = stock.history(period="1y", interval="1d")

# 检查数据是否为空
if data.empty:
    print("No data found for MSFT. Please check the ticker or try a different period.")
    exit()

# 计算SMA（简单移动平均）
data['SMA50'] = data['Close'].rolling(window=50).mean()

# 识别杯柄形态
def bowl(x, a, b, c):
    """二次曲线拟合函数，用于识别杯形底部"""
    return a * (x - b)**2 + c

def find_bowl(data):
    """通过曲线拟合来寻找杯形底部"""
    x = np.arange(len(data))
    y = data['Close'].values

    # 选择拟合的范围
    fit_data = data.iloc[-60:]  # 只用最后60天的数据
    x_fit = np.arange(len(fit_data))
    y_fit = fit_data['Close'].values

    # 曲线拟合
    popt, _ = curve_fit(bowl, x_fit, y_fit, p0=[0.1, len(fit_data)//2, min(y_fit)])

    return popt, fit_data

# 获取杯形底部的拟合参数
params, fit_data = find_bowl(data)

# 绘制股价和拟合的曲线
plt.figure(figsize=(10, 6))
plt.plot(data['Close'], label='Close Price')
plt.plot(fit_data.index, bowl(np.arange(len(fit_data)), *params), label='Fitted Bowl', linestyle='--')
plt.title('MSFT Stock Price with Cup and Handle Pattern (Fitted)')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# 识别突破点
def identify_breakout(data, volume_threshold=1.5):
    """识别杯柄突破点，考虑成交量"""
    breakout_points = []

    for i in range(1, len(data)):
        # 突破条件：价格突破50日移动平均线且成交量放大
        if data['Close'].iloc[i] > data['SMA50'].iloc[i] and data['Volume'].iloc[i] > volume_threshold * data['Volume'].iloc[i-1]:
            breakout_points.append(data.index[i])

    return breakout_points

# 识别突破点
breakout_points = identify_breakout(data)

# 绘制股价图表和突破点
plt.figure(figsize=(10, 6))
plt.plot(data['Close'], label='Close Price')
plt.scatter(breakout_points, data.loc[breakout_points]['Close'], color='red', label='Breakout Points')
plt.title('MSFT Stock Price with Breakout Points')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

from ib_insync import *
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # 或者 'Qt5Agg'
import yaml

config_file = '../config.yml'

# 读取YAML配置文件
with open(config_file, 'r', encoding='utf-8', errors='ignore') as file:
    config = yaml.safe_load(file)

# 恐慌指数VIX查询
# 连接 TWS（模拟账户端口 7497，真实账户端口 4002）
ib = IB()
ib.connect(config['IBKR']['ip'], config['IBKR']['port'], clientId=8, timeout=30)

# 获取 VIX 指数数据
vix = Index(symbol='VIX', exchange='CBOE')
ib.qualifyContracts(vix)

# 获取历史数据（最近 30 天，每天一条数据）
bars = ib.reqHistoricalData(
    vix,
    endDateTime='',
    durationStr='60 D',  # 90 天数据
    barSizeSetting='1 day',  # 日线数据
    whatToShow='TRADES',  # 获取 VIX 的中间价
    useRTH=True  # 仅使用 RTH（常规交易时段）数据
)

# 断开连接
ib.disconnect()

# 提取日期和收盘价
dates = [bar.date for bar in bars]
prices = [bar.close for bar in bars]

# 绘制 VIX 走势图
plt.figure(figsize=(10, 5))
plt.plot(dates, prices, label='VIX Index', color='red')
plt.xlabel('Date')
plt.ylabel('VIX Value')
plt.title('VIX Index Trend (Last 30 Days)')
plt.legend()
plt.grid()
plt.show()

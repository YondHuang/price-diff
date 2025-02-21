import pandas as pd
from ib_insync import Stock
from utils.ExtrsUtil import ExtrsUtil
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import BarData
import time

class IBWrapper(EWrapper):
    def __init__(self):
        self.data = []

    def error(self, reqId, errorCode, errorString):
        """ 错误处理回调 """
        print(f"Error encountered: reqId={reqId}, code={errorCode}, message={errorString}")

    def historicalData(self, reqId, bar: BarData):
        """ 收到历史数据时调用的函数 """
        print(f"Received data: {bar.date}, Close: {bar.close}")  # 打印每个数据点
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        """ 历史数据结束时调用 """
        print(f"Historical data request completed for reqId: {reqId}, from: {start} to: {end}")

class IBClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


# 设置 IBKR 客户端
def fetch_data_from_ib():
    # 创建客户端和 wrapper
    wrapper = IBWrapper()
    client = IBClient(wrapper)

    # 连接到 IB API (本地 TWS 或 IB Gateway)
    client.connect("127.0.0.1", 7496, 0)

    if client.isConnected():
        print("Connected to IBKR")
    else:
        print("Failed to connect to IBKR")
        return None

    try:
        print("Requesting historical data...")
        # 请求苹果股票的历史数据，获取过去 30 天的数据，时间间隔为 1 天
        contract = Stock('AAPL', 'NASDAQ', 'USD')  # 定义股票合约
        client.reqHistoricalData(1,
                                 contract,
                                 endDateTime='',
                                 durationStr='5 D',
                                 barSizeSetting='1 day',
                                 whatToShow='MIDPOINT',
                                 useRTH=False,  # 获取全天数据
                                 formatDate=1,
                                 keepUpToDate=False,
                                 chartOptions=[]  # 添加空的 chartOptions 参数
                                 )

        # 等待数据返回
        print("Waiting for data...")
        time.sleep(5)

        # 打印当前数据
        print(f"Current data: {wrapper.data}")

        # 将历史数据转换为 DataFrame
        if wrapper.data:
            df = pd.DataFrame(wrapper.data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Date'] = pd.to_datetime(df['Date'])
            return df
        else:
            print("No data received.")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        client.disconnect()

# 获取数据
df = fetch_data_from_ib()

# 创建 ExtrsUtil 实例
util = ExtrsUtil()

# 假设 N = 3，调用 extrs 函数计算 EXTRS
N = 3
df['EXTRS'] = util.extrs(df, N)

# 输出结果
print(df)
from ib_insync import IB
from ibapi.client import EClient
from ibapi.contract import Contract
from datetime import datetime

ib = IB()
ib.connect('104.194.79.173', 4001, clientId=1, timeout=30)  # 7497 是纸交易端口，7496 是真实交易端口

# 获取当前日期，时间设置为 00:00:00
current_datetime = datetime.utcnow().date()
end_time = current_datetime.strftime('%Y%m%d-00:00:00')  # 格式化为指定格式

# 创建股票合约
contract = Contract()
contract.symbol = 'ASO'
contract.secType = 'STK'
contract.exchange = 'SMART'
contract.currency = 'USD'

# 请求历史数据
bars = ib.reqHistoricalData(
    reqId=1,  # 唯一的请求标识符
    contract=contract,
    endDateTime=end_time,
    durationStr='5 D',  # 获取过去 1 天的数据
    barSizeSetting='1 day',  # 每天的数据
    whatToShow='TRADES',
    useRTH=True,
    formatDate=1,
    keepUpToDate=False,  # 不需要实时更新
    chartOptions=[]  # 空的图表选项
)
print(f"bars",bars)
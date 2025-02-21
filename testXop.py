from ib_insync import *

ib = IB()

# 连接到TWS或IB Gateway（默认端口为7497）。端口7497: 模拟账户（模拟环境），实盘环境为7496
ib.connect('127.0.0.1', 7496, clientId=1)

print("连接成功" if ib.isConnected() else "连接失败")


# 查看当前账户信息
accounts = ib.managedAccounts()
print(f"当前账户: {accounts}")

# 创建一个合约
# contract = Stock('AAPL', 'SMART', 'USD')
contract = Stock('XOP', 'SMART', 'USD')

# 请求市场数据（可以设置延时模式）
#ticker = ib.reqMktData(contract, regulatorySnapshot=False)
ticker = ib.reqMktData(contract)

# 等待数据返回
ib.sleep(2)  # 等待 2 秒获取数据

print(ticker)

# 输出 KWEB 最新价格
if ticker.last:
    print(f"KWEB 最新价格: {ticker.last}")
elif ticker.close:
    print(f"KWEB 收盘价格（延时数据）: {ticker.close}")
else:
    print("未能获取实时或延迟数据，请检查市场数据订阅。")

# 断开连接
ib.disconnect()
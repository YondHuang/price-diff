from ib_insync import *

ib = IB()

# 连接到TWS或IB Gateway（默认端口为7497）。端口7497: 模拟账户（模拟环境），实盘环境为7496
ib.connect('127.0.0.1', 7497, clientId=1)

print("连接成功" if ib.isConnected() else "连接失败")

# 获取账户总结信息
account_summary = ib.accountSummary()
for item in account_summary:
    print(item)

# 查看当前账户信息
accounts = ib.managedAccounts()
print(f"当前账户: {accounts}")

# 创建一个合约
# contract = Stock('AAPL', 'SMART', 'USD')
contract = Stock('KWEB', 'SMART', 'USD')

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



# # 定义期货合约模板
# contract = Future('ES', '', 'GLOBEX')  # 不指定合约日期，查询所有合约
#
# # 查询合约详情
# futures = ib.reqContractDetails(contract)
#
# if futures:
#     # 获取主力合约
#     main_contract = futures[0].contract
#     print(f"主力合约: {main_contract.localSymbol}")
#
#     # 获取市场数据
#     ticker = ib.reqMktData(main_contract)
#     ib.sleep(2)
#     print(f"最新价格: {ticker.last}")
#     print(f"买价: {ticker.bid}, 卖价: {ticker.ask}")    # 买卖报价
# else:
#     print("未找到符合条件的合约")


# 打印实时数据
# print(f"当前价格: {ticker.last}")

# 创建订单（限价买入）
order = LimitOrder('BUY', 10, ticker.last + 0.01)  # 买入10股，每股价格150美元
# 下单
trade = ib.placeOrder(contract, order)

# 查看订单状态
print(f"订单状态: {trade.orderStatus.status}")
print(f"成交数量: {trade.orderStatus.filled}, 剩余数量: {trade.orderStatus.remaining}")
print(f"限价: {trade.order.lmtPrice}")

ib.sleep(2)

# 获取所有已提交订单
trades = ib.trades()
for trade in trades:
    print(f"订单状态: {trade.orderStatus.status}, 成交数量: {trade.orderStatus.filled}, 剩余数量: {trade.orderStatus.remaining}")


# 获取未完成订单
open_trades = ib.openTrades()
if open_trades:
    for trade in open_trades:
        print(f"未完成订单状态: {trade.orderStatus.status}, 限价: {trade.order.lmtPrice}")
else:
    print("没有未完成的订单。")

# 查看账户持仓
positions = ib.positions()

# 输出当前持仓
for position in positions:
    print(f"合约: {position.contract.symbol}, 持仓量: {position.position}")

# account_summary = ib.accountSummary()
# for item in account_summary:
#     print(item)

# 断开连接
ib.disconnect()




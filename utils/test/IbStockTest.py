from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class IBAPI(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def contractDetails(self, reqId, contractDetails):
        print(f"Contract Details: {contractDetails}")

    def error(self, reqId, errorCode, errorString):
        print(f"Error: {errorCode} - {errorString}")

def get_stock_details(symbol):
    app = IBAPI()
    app.connect("127.0.0.1", 7496, 0)  # 连接到 TWS 或 IB Gateway

    # 创建股票合约对象
    contract = Contract()
    contract.symbol = symbol  # 股票的 Symbol (例如：AAPL)
    contract.secType = "STK"  # 股票
    contract.exchange = "98954M101"  # 使用 SMART 作为默认交易所
    contract.currency = "USD"

    # 请求股票的合约详细信息
    app.reqContractDetails(1, contract)
    app.run()

if __name__ == "__main__":
    get_stock_details("AAPL")  # 可以通过 ISIN 确定 Symbol，然后查询

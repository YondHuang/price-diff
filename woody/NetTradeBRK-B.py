import time
import yfinance as yf
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import pytz
from datetime import datetime


class MyEWrapper(EWrapper):
    def __init__(self, client):
        self.client = client
        self.symbol = 'BRK B'  # 在IB中交易 BRK B
        self.grid_percent = 0.005  # 网格间隔设为 0.5%
        self.grid_orders = [460.0, 465.0, 470.0, 475.0, 480.0]  # 初始价格网格
        self.buy_pos = 0  # 当前买入位置
        self.sell_pos = 0  # 当前卖出位置
        self.last_price = None

    def nextValidId(self, orderId: int):
        # 使用 Yahoo Finance 获取 BRK-B 实时数据
        self.get_yahoo_data()

    def get_yahoo_data(self):
        try:
            # 判断当前是否为美国股市的交易时间
            # 获取当前中国时间（CST）
            china_time = datetime.now(pytz.timezone('Asia/Shanghai'))

            # 转换为美国东部时间（EST）
            eastern = pytz.timezone('US/Eastern')
            eastern_time = china_time.astimezone(eastern)

            # 美国股市交易时间：9:30 AM - 4:00 PM EST
            market_open = eastern_time.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = eastern_time.replace(hour=16, minute=0, second=0, microsecond=0)

            if market_open <= eastern_time <= market_close:
                # 从 Yahoo Finance 获取 BRK-B 实时数据
                stock = yf.Ticker("BRK-B")  # 雅虎财经使用 BRK-B
                stock_info = stock.info
                
                # 获取最新的实时价格
                if 'regularMarketPrice' not in stock_info:
                    print("No real-time price available for BRK-B from Yahoo Finance.")
                    return
                
                self.last_price = stock_info['regularMarketPrice']  # 获取实时价格
                print(f"Last price for {self.symbol} from Yahoo Finance: {self.last_price}")
                self.check_grid_and_execute()
            else:
                print(f"Market is closed. Current time in US/Eastern: {eastern_time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"Error fetching data from Yahoo Finance: {e}")
            self.last_price = None  # 设为 None，表示获取数据失败

    def check_grid_and_execute(self):
        if self.last_price is None:
            return

        # 获取当前网格价格
        buy_price = self.grid_orders[self.buy_pos]
        sell_price = self.grid_orders[self.sell_pos]

        grid_step = buy_price * self.grid_percent

        # 如果价格低于买入网格，执行买入操作
        if self.last_price <= buy_price - grid_step:
            self.execute_trade('BUY', self.last_price)
            self.buy_pos = (self.buy_pos + 1) % len(self.grid_orders)

        # 如果价格高于卖出网格，执行卖出操作
        elif self.last_price >= sell_price + grid_step:
            self.execute_trade('SELL', self.last_price)
            self.sell_pos = (self.sell_pos + 1) % len(self.grid_orders)

    def execute_trade(self, action, price):
        order = Order()
        order.action = action
        order.totalQuantity = 100  # 假设每次交易 100 股
        order.orderType = 'LMT'
        order.lmtPrice = price
        #self.client.placeOrder(self.client.order_id, self.create_contract(), order)
        print(f"self.client.order_id : {self.client.order_id}, self.create_contract() : {self.create_contract()}, order : {order}")

    def create_contract(self):
        contract = Contract()
        contract.symbol = self.symbol
        contract.secType = 'STK'
        contract.currency = 'USD'
        contract.exchange = 'SMART'
        return contract


class MyEClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)
        self.wrapper = wrapper
        self.order_id = 1

    def placeOrder(self, orderId, contract, order):
        # 这里是下单的实际过程，使用 IB API 下单
        print(f"Placing order {orderId} for {contract.symbol} {order.action} {order.totalQuantity} shares at {order.lmtPrice}")
        self.order_id += 1


# 初始化客户端
app = MyEClient(MyEWrapper(None))
app.wrapper = MyEWrapper(app)
# app.connect('127.0.0.1', 7497, clientId=1)
app.connect('104.194.79.173', 4001, clientId=1)

time.sleep(1)

# 运行之前获取市场数据
app.wrapper.get_yahoo_data()

app.run()

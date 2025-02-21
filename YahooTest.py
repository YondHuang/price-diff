import yfinance as yf

from utils.InstitutionHold import InstitutionHold

# 获取某只股票的信息，举例：Apple (AAPL)
stock = yf.Ticker("AAPL")

# 获取股东持股数据
holders = stock.major_holders

# 输出前几位股东的持股比例（通常包括机构股东）
print("Institutional holders:")
print(holders)


# 示例股票列表
stock_list = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]

# 筛选符合条件的股票
iHinstance = InstitutionHold()
selected_stocks = [stock for stock in stock_list if iHinstance.checkInstitutionalFloatPercentHeld(stock, 0.6)]
print(f"Selected stocks with institutional ownership > 60%: {selected_stocks}")

selected_stocks = [stock for stock in stock_list if iHinstance.checkInstitutionalCount(stock, 500, 6000)]
print(f"Selected stocks with institutional count in (500, 6000): {selected_stocks}")
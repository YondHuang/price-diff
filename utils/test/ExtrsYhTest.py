import yfinance as yf
import pandas as pd
from utils.ExtrsUtil import ExtrsUtil
from plugins.YahooFin import YahooFin
from data.DataBase import DataBase

# 从 Yahoo Finance 获取 AAPL 股票的历史数据
symbol = 'AAPL'
ins = YahooFin()
df = ins.fetchData(symbol, period='1mo', interval='1d')

# 打印获取到的数据
print("Fetched data:")
print(df)

# 示例股票列表
#stock_symbols = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA']
sina_config_file = '../../config.yml'
dataIns = DataBase(sina_config_file)
stock_symbols = dataIns.getCommonData('stock_basic', ['code'], {}, '', '')
extrs_util = ExtrsUtil()

# 计算 EXTRS 指标
# N = 5  # 设置计算 EXTRS 的 N 天
# df = extrs_util.extrs(df, N=5)
#
# # 打印带有 EXTRS 的数据
# print("\nData with EXTRS:")
# print(df)
#print(stock_symbols)
# 使用列表推导式提取 code 的值
symbols = [item['code'] for item in stock_symbols]
print(symbols)


# # 获取排名
# ranked_stocks = extrs_util.extrsRank(symbols, N=5)
# # 打印排名结果
# print("\nRanked Stocks by EXTRS:")
# for rank, (symbol, extrs_score) in enumerate(ranked_stocks, start=1):
#     print(f"{rank}. {symbol}: {extrs_score:.2f}")

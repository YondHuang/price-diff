import logging
import logging.config
import ctypes
import yfinance as yf
import pandas as pd
import os
import shutil
from utils.ExtrsUtil import ExtrsUtil
from plugins.YahooFin import YahooFin
from data.DataBase import DataBase


import sys
sys.setrecursionlimit(10000)  # 限制递归深度
print(yf.version)

# 加载配置文件
logging.config.fileConfig('../../logging.conf')

"""
查询指定名称的股票代码，把最近一天日期的价格数据都写入数据库stock_record
"""
sina_config_file = '../../config.yml'
dataIns = DataBase(sina_config_file)

# 设置栈空间为 10 MB
#ctypes.windll.kernel32.SetThreadStackGuarantee(ctypes.c_ulong(10 * 1024 * 1024))

# 示例股票列表
# sql = "select DISTINCT code from stock_basic where is_closed=0 and code not in (SELECT code from stock_record where c_date='2025-02-10')"
# stock_symbols = dataIns.getSqlData(sql)
# symbols = [item['code'] for item in stock_symbols]

# query_conditions = {"is_closed": 0}
# stock_symbols = dataIns.getCommonData('stock_basic', ['code'], query_conditions, '', '')
# symbols = [item['code'] for item in stock_symbols]
#print(stock_symbols)


# 使用列表推导式提取 code 的值

symbols = [
    # 'NR',
    # 'RADR',
    # 'VVI',
    # 'BRK.AQ',
]
print(symbols)

# 创建一个空列表，用于存储所有股票的信息
values = []

## 写入数据库
fields = ['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']

# 清除缓存
import shutil

cache_dir = os.path.expanduser("~/.yfinance_cache")
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)  # 删除缓存目录
    print("yfinance 缓存已清除")

for symbol in symbols:
    print(f"Fetching data for {symbol}...")
    yfIns = YahooFin()
    """
    ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'ytd', 'max']
    1d（1天）表示获取当天的历史数据，通常按分钟或更细粒度的间隔提供数据（如果可用）。
    5d（5天）表示获取过去 5 天的数据，通常是按分钟、小时或日间隔的数据。
    1mo（1个月）获取过去 1 个月的数据，通常按日间隔。
    3mo（3个月）获取过去 3 个月的数据，通常按日间隔。
    6mo（6个月）获取过去 6 个月的数据，按日间隔。
    1y（1年）获取过去 1 年的数据，按日间隔。
    2y（2年）获取过去 2 年的数据，按日间隔。
    5y（5年）获取过去 5 年的数据，按日间隔。
    ytd（Year-to-Date）获取从今年年初到当前日期的数据。时间间隔通常为按日。
    max（最大可用范围）获取该资产可以追溯到的最早时间的数据，直到当前日期。
    """
    #df = yfIns.fetchData(symbol, period='1d', interval='1d')
    startDate = '2025-02-11'
    endDate = '2025-02-15'
    df = yfIns.fetchStartEndData(symbol, startDate, endDate, interval='1d')
    pd.set_option('display.max_columns', None)  # 显示所有列
    pd.set_option('display.width', 1000)        # 设置显示宽度
    # print(df.index)
    # print(df.columns)
    # print(df)

    if df.empty:  # 检查数据是否为空
        print(f"No data found for {symbol}. Skipping...")
        logging.error(f"No data found for {symbol}. Skipping...")
        continue

    # 处理 DataFrame
    df["code"] = symbol  # 添加 code 列
    # 重置索引，将时间字段转为普通列
    df = df.reset_index()

    # 重命名时间字段
    # df.rename(columns={"index": "Date"}, inplace=True)

    # print(df)
    # 提取日期部分
    df["c_date"] = pd.to_datetime(df["Date"]).dt.date
    df.rename(columns={"Date": "remark"}, inplace=True)
    # print(df)

    # 删除不需要的列
    df = df.drop(columns=["Dividends", "Stock Splits"])
    # 重新排列列的顺序
    desired_order = ["code", "c_date", "Open", "High", "Low", "Close", "Volume", "remark"]
    df = df[desired_order]

    # 将列名映射到数据库字段名
    column_mapping = {
        "Open": "o_price",
        "High": "h_price",
        "Low": "l_price",
        "Close": "c_price",
        "Volume": "vol"
    }
    df.rename(columns=column_mapping, inplace=True)

    # 检查数据类型
    # print(df.dtypes)

    # 替换 NaN 为 None，避免 MySQL 插入时报错
    df[['o_price', 'h_price', 'l_price', 'c_price']] = df[['o_price', 'h_price', 'l_price', 'c_price']].fillna(0)
    print(df)

    # 检查哪些列中存在 NaN
    # print(df.isna().sum())

    # 筛选出包含 NaN 的行
    # print(df[df.isna().any(axis=1)])

    # 转换为符合批量插入格式的 values
    values = df[['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']].values.tolist()
    print(values)

    dataIns.saveBatchCommonData('stock_record', fields, values)


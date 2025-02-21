from utils.ExtrsUtil import ExtrsUtil
import pandas as pd
from data.DataBase import DataBase

"""
查询数据库所有stock_basic的股票代码，从stock_record得到价格数据，计算extra_val值后把数据都写入数据库stock_extra
"""

# 调用函数计算 EXTRS，假设 N = 50 , 150, 250
N = 50

sina_config_file = '../../config.yml'
dataIns = DataBase(sina_config_file)
# stock_symbols = dataIns.getCommonData('stock_basic', ['code'], {}, '', '')
sql = f"select DISTINCT code from stock_record where code not in (select DISTINCT code from stock_extra where num=50)"
stock_symbols = dataIns.getSqlData(sql)
symbols = [item['code'] for item in stock_symbols]

# symbols = {'ALLR',}
# print(symbols)

## 写入数据库字段
fields = ['code', 'c_date', 'ref_c', 'num', 'extra_val']

# 计算extra的值
ins = ExtrsUtil()

for symbol in symbols:
    print(f"Fetching data for {symbol}...")
    query_conditions = {"code": symbol}
    data = dataIns.getCommonData('stock_record', ['code', 'c_date', 'c_price'], query_conditions, '', '')
    # print(data)


    df = ins.extrs(data, N)
    df = df.drop(columns=["c_price"])

    print(df)
    values = df[['code', 'c_date', 'ref_c', 'num', 'extra_val']].values.tolist()

    #写入数据库
    dataIns.saveBatchCommonData('stock_extra', fields, values)
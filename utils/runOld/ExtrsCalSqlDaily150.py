from utils.ExtrsUtil import ExtrsUtil
import pandas as pd
from data.DataBase import DataBase
from datetime import datetime, timedelta

"""
查询数据库所有stock_basic的股票代码，从stock_record得到价格数据，计算extra_val值后把数据都写入数据库stock_extra
"""

# 调用函数计算 EXTRS，假设 N = 3
N = 150

# 获取当前日期
current_date = datetime.now()
previous_date = current_date - timedelta(days=1)

# 格式化日期为 'YYYY-MM-DD'
formatted_date = previous_date.strftime('%Y-%m-%d')
formatted_date = '2025-02-21'

config_file = '../../config.yml'
dataIns = DataBase(config_file)
inWhere = f"(select code from stock_extra where c_date='{formatted_date}' and num = 150)"
stock_symbols = dataIns.getCommonInData('stock_basic', ['code'], False, 'code', inWhere, {})

symbols = [item['code'] for item in stock_symbols]
print(symbols)
print(len(symbols))

# 计算extra的值
ins = ExtrsUtil()
## 写入数据库字段
fields = ['code', 'c_date', 'ref_c', 'num', 'extra_val']

for symbol in symbols:
    print(f"Fetching data for {symbol}...")
    query_conditions = {"code": symbol, "c_date": ("<=", formatted_date)}# 小于等于条件
    data = dataIns.getCommonData('stock_record', ['code', 'c_date', 'c_price'], query_conditions, 'c_date desc', f"{N+1}")
    # print(data)

    if data:
        df = ins.extrs(data, N)
        df = df.drop(columns=["c_price"])

        print(df)
        values = df[['code', 'c_date', 'ref_c', 'num', 'extra_val']].values.tolist()

        #写入数据库
        dataIns.saveBatchCommonData('stock_extra', fields, values)
from utils.ExtrsUtil import ExtrsUtil
import pandas as pd
from data.DataBase import DataBase

# 调用函数计算 EXTRS，假设 N = 3
N = 250

sina_config_file = '../../config.yml'
dataIns = DataBase(sina_config_file)

stock_symbols = [{'code': 'ADT'},{'code': 'ATGE'}]
symbols = [item['code'] for item in stock_symbols]
print(symbols)

## 写入数据库字段
fields = ['code', 'c_date', 'ref_c', 'num', 'extra_val']

for symbol in symbols:
    print(f"Fetching data for {symbol}...")
    query_conditions = {"code": symbol}
    data = dataIns.getCommonData('stock_record', ['code', 'c_date', 'c_price'], query_conditions, 'c_date desc', f"{N+1}")
    print(data)

    # 计算extra的值
    ins = ExtrsUtil()
    df = ins.extrs(data, N)
    df = df.drop(columns=["c_price"])

    print(df)
    values = df[['code', 'c_date', 'ref_c', 'num', 'extra_val']].values.tolist()

    #写入数据库
    dataIns.saveBatchCommonData('stock_extra', fields, values)
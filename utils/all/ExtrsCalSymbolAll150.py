from utils.ExtrsUtil import ExtrsUtil
import pandas as pd
from data.DataBase import DataBase
import numpy as np

# 调用函数计算 EXTRS，假设 N = 3
N = 150

sina_config_file = '../../config.yml'
dataIns = DataBase(sina_config_file)

stock_symbols = [{'code': 'FI'}]
symbols = [item['code'] for item in stock_symbols]
print(symbols)

## 写入数据库字段
fields = ['code', 'c_date', 'ref_c', 'num', 'extra_val']

for symbol in symbols:
    print(f"Fetching data for {symbol}...")
    query_conditions = {"code": symbol}
    data = dataIns.getCommonData('stock_record', ['code', 'c_date', 'c_price'], query_conditions, '', '')
    # print(data)

    # 计算extra的值
    ins = ExtrsUtil()
    df = ins.extrs(data, N)
    df = df.drop(columns=["c_price"])

    # 设置 Pandas 显示选项，确保所有行都被打印出来
    pd.set_option('display.max_rows', None)  # 显示所有行
    pd.set_option('display.max_columns', None)  # 显示所有列
    pd.set_option('display.width', None)  # 自动换行显示，避免行被截断

    print(df)
    values = df[['code', 'c_date', 'ref_c', 'num', 'extra_val']].values.tolist()

    # 筛选出包含 inf 或 -inf 的行
    df_with_inf = df[df.isin([np.inf, -np.inf]).any(axis=1)]

    # 打印包含 inf 或 -inf 的行
    # print("\n包含 inf 或 -inf 的行:")
    # print(df_with_inf)

    #写入数据库
    dataIns.saveBatchCommonData('stock_extra', fields, values)
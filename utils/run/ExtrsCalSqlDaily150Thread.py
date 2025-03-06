import time
import concurrent.futures
from utils.ExtrsUtil import ExtrsUtil
import pandas as pd
from data.DataBase import DataBase
from datetime import datetime, timedelta

"""
查询数据库所有stock_basic的股票代码，从stock_record得到价格数据，计算extra_val值后把数据都写入数据库stock_extra
"""

# 调用函数计算 EXTRS，假设 N = 150
N = 150

# 获取当前日期
current_date = datetime.now()
previous_date = current_date - timedelta(days=1)

# 格式化日期为 'YYYY-MM-DD'
formatted_date = previous_date.strftime('%Y-%m-%d')
formatted_date = '2025-03-04'

config_file = '../../config.yml'
dataIns = DataBase(config_file)
inWhere = f"(select code from stock_extra where c_date='{formatted_date}' and num = {N})"
print(inWhere)
stock_symbols = dataIns.getCommonInData('stock_basic', ['code'], False, 'code', inWhere, {})

symbols = [item['code'] for item in stock_symbols]
print(symbols)
print(len(symbols))

# 计算extra的值
ins = ExtrsUtil()

# 定义写入数据库的字段
fields = ['code', 'c_date', 'ref_c', 'num', 'extra_val']

# 定义并行执行的函数
def process_symbol(symbol):
    try:
        print(f"Fetching data for {symbol}...")
        query_conditions = {"code": symbol, "c_date": ("<=", formatted_date)}  # 小于等于条件
        data = dataIns.getCommonData('stock_record', ['code', 'c_date', 'c_price'], query_conditions, 'c_date desc', f"{N + 1}")
        print(f"Fetched data for {symbol}: {len(data)} records.")

        if data:
            # 计算 extra 值
            df = ins.extrs(data, N)
            df = df.drop(columns=["c_price"])  # 删除价格列

            print(f"Processed data for {symbol}")
            values = df[['code', 'c_date', 'ref_c', 'num', 'extra_val']].values.tolist()
            print(values)

            # 写入数据库
            dataIns.saveBatchCommonData('stock_extra', fields, values)
            print(f"Saved data for {symbol}")

        else:
            print(f"No data found for {symbol}. Skipping...")

    except Exception as e:
        print(f"Error while processing {symbol}: {e}")

# 使用线程池并行处理股票数据
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for symbol in symbols:
        futures.append(executor.submit(process_symbol, symbol))

    # 等待所有任务完成
    concurrent.futures.wait(futures)

print("All tasks completed.")

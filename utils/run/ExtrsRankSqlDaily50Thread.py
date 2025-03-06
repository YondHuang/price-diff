import time
import concurrent.futures
from utils.ExtrsUtil import ExtrsUtil
import pandas as pd
from data.DataBase import DataBase
from datetime import datetime, timedelta

"""
查询数据库所有stock_basic的股票代码，从stock_record得到价格数据，计算extra_val值后把数据都写入数据库stock_extra
"""

# 调用函数计算 EXTRS，假设 N = 50, 150, 250
N = 50

config_file = '../../config.yml'
dataIns = DataBase(config_file)

# 获取当前日期
current_date = datetime.now()
previous_date = current_date - timedelta(days=1)

# 格式化日期为 'YYYY-MM-DD'
formatted_date = previous_date.strftime('%Y-%m-%d')

# dateArr = {formatted_date}
dateArr = {'2025-02-27','2025-02-28','2025-03-03','2025-03-04'}
print(dateArr)

# 写入数据库字段
fields = ['code', 'c_date', 'extra_val', 'num', 'rank_val']
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列

def process_date(cDate):
    try:
        print(f"Fetching data for {cDate}...")
        conditions = {"c_date": cDate, "num": N}
        data = dataIns.getCommonData('stock_extra', ['code', 'extra_val', 'num', 'c_date'], conditions, '', '')
        df = pd.DataFrame(data)

        if df.empty:
            print(f"No data found for {cDate}. Skipping...")
            return

        # 计算 extra 值
        ins = ExtrsUtil()
        df = ins.extrsRank(df)

        print(f"Processed data for {cDate}")
        values = df[['code', 'c_date', 'extra_val', 'num', 'rank_val']].values.tolist()
        print(values)

        # 写入数据库
        dataIns.saveBatchCommonData('stock_extra_rank', fields, values)
        print(f"Saved data for {cDate}")

    except Exception as e:
        print(f"Error while processing {cDate}: {e}")

# 使用线程池并行处理每个日期的数据
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_date, cDate) for cDate in dateArr]

    # 等待所有任务完成
    concurrent.futures.wait(futures)

print("All tasks completed.")

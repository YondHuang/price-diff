from utils.ExtrsUtil import ExtrsUtil
import pandas as pd
from data.DataBase import DataBase
from datetime import datetime, timedelta

"""
查询数据库所有stock_basic的股票代码，从stock_record得到价格数据，计算extra_val值后把数据都写入数据库stock_extra
"""

# 调用函数计算 EXTRS，假设 N = 50 , 150, 250
N = 250

config_file = '../../config.yml'
dataIns = DataBase(config_file)

# query_conditions = {"num": N}
# dates = dataIns.getDistinctCommonData('stock_extra', ['c_date'], query_conditions, 'c_date asc', '')
# # 使用列表推导式提取 code 的值
# dateArr = [item['c_date'] for item in dates]

# 获取当前日期
current_date = datetime.now()
previous_date = current_date - timedelta(days=1)

# 格式化日期为 'YYYY-MM-DD'
formatted_date = previous_date.strftime('%Y-%m-%d')

dateArr = {
    formatted_date
}
print(dateArr)

## 写入数据库字段
fields = ['code', 'c_date', 'extra_val', 'num', 'rank_val']
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列

for cDate in dateArr:
    print(f"Fetching data for {cDate}...")
    conditions = {"c_date": cDate, "num": N}
    data = dataIns.getCommonData('stock_extra', ['code', 'extra_val', 'num', 'c_date'], conditions, '', '')
    df = pd.DataFrame(data)
    # print(df)

    # 计算extra的值
    ins = ExtrsUtil()
    df = ins.extrsRank(df)

    print(df)
    values = df[['code', 'c_date', 'extra_val', 'num', 'rank_val']].values.tolist()

    # print(values)

    #写入数据库
    dataIns.saveBatchCommonData('stock_extra_rank', fields, values)
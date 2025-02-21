from utils.ExtrsUtil import ExtrsUtil
import pandas as pd
from data.DataBase import DataBase

"""
查询数据库所有stock_basic的股票代码，从stock_record得到价格数据，计算extra_val值后把数据都写入数据库stock_extra
"""

data = {'extra_val': [1, 1, 2, 2, 2, 3, 3, 5, 6, 7, 8, 9, 10]}
df = pd.DataFrame(data)

# 计算extra的值
ins = ExtrsUtil()
df = ins.extrsRank(df)

print(df)

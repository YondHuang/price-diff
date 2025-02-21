from utils.ExtrsUtil import ExtrsUtil
import pandas as pd

# 示例数据：假设 df 是一个包含历史收盘价的 DataFrame
data = {
    'Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
    'Close': [100, 105, 110, 108, 115]
}

df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])

# 调用函数计算 EXTRS，假设 N = 3
N = 3

ins = ExtrsUtil()
df['EXTRS'] = ins.extrs(df, N)

print(df)
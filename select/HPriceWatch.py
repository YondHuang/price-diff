import pandas as pd
from data.DataBase import DataBase
import decimal

# 数据库查询
sina_config_file = '../config.yml'
dataIns = DataBase(sina_config_file)

N = 250
query_conditions = {"c_date": '2025-02-07'}
data = dataIns.getCommonData('stock_record', ['code', 'c_price', 'h_price', 'l_price', 'c_date'], query_conditions, 'c_date desc', f"{N+1}")

df = pd.DataFrame(data)

# **数据转换**
data = [
    {key: float(value) if isinstance(value, decimal.Decimal) else value for key, value in row.items()}
    for row in data
]

print(df)

# **1. 计算 过去20天内最高价 及 新高天数**
df["最高价_20"] = df.groupby("code")["h_price"].transform(lambda x: x.rolling(20).max())
df["新高天数"] = df.groupby("code")["h_price"].transform(lambda x: x.rolling(20).apply(lambda y: 20 - y.argmax(), raw=True))

# **2. 计算 新低天数**
df["新低天数"] = df.groupby("code")["l_price"].transform(lambda x: x.rolling(20).apply(lambda y: (y.argmin() if y.min() < y.max() else 0), raw=True))

# **3. 计算 新高价 和 新低价**
def get_shifted_value(row, price_series, shift_series):
    shift_val = row[shift_series]
    if pd.isna(shift_val) or shift_val < 0 or shift_val >= len(price_series):
        return None  # 避免索引越界
    return price_series.iloc[int(shift_val)]  # 确保整数索引

# **使用 apply 逐行计算新高价和新低价**
df["新高价"] = df.apply(lambda row: get_shifted_value(row, df[df["code"] == row["code"]]["h_price"], "新高天数"), axis=1)
df["新低价"] = df.apply(lambda row: get_shifted_value(row, df[df["code"] == row["code"]]["l_price"], "新低天数"), axis=1)

# **4. 计算 回撤幅度**
df["回撤幅度"] = (df["新高价"] - df["新低价"]) / df["新高价"]

# **5. 计算 SXHCG31**
df["SXHCG31"] = (df["回撤幅度"] <= 0.3) & df.groupby("code")["回撤幅度"].transform(lambda x: (x > 0.3).rolling(20).sum() == 0)

# 计算过去 250 天的最高收盘价
df["最高收盘价_250"] = df.groupby("code")["c_price"].transform(lambda x: x.rolling(250, min_periods=1).max())

print(df)

# 计算 SXHCG32
df["SXHCG32"] = df.groupby("code")["c_price"].transform("first") / df["最高收盘价_250"] > 0.5

# 选出符合条件的股票
selected_stocks = df[df["SXHCG32"]][["code", "c_date", "c_price"]]

print("SXHCG32", selected_stocks)

# **8. 计算 SXHCG3**
df["SXHCG3"] = df["SXHCG31"] & df["SXHCG32"]

# **9. 选出符合条件的股票**
selected_stocks = df[df["SXHCG3"]][["code", "c_date", "c_price"]]

# **输出**
print(selected_stocks)

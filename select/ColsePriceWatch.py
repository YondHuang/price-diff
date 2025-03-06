import pandas as pd
from data.DataBase import DataBase

config_file = '../config.yml'
dataIns = DataBase(config_file)

N = 250
# query_conditions = {"c_date": '2025-02-07'}
# data = dataIns.getCommonData('stock_record', ['code', 'c_price', 'c_date'], query_conditions, 'c_date desc', f"{N+1}")
data = dataIns.getSqlData(f"WITH ranked_data AS ( "
                          f"SELECT "
                          f"code, c_price, h_price, l_price, c_date, "
                          f"ROW_NUMBER() OVER (PARTITION BY code ORDER BY c_date DESC) AS row_num "
                          f"FROM stock_record "
                          f") "
                          f"SELECT code, c_price, h_price, l_price, c_date "
                          f"FROM ranked_data "
                          f"WHERE row_num <= 250;")

df = pd.DataFrame(data)
print(df)

# 转换为 Pandas DataFrame

# 计算均线
df["MA_10"] = df.groupby("code")["c_price"].transform(lambda x: x.rolling(10).mean())
df["MA_20"] = df.groupby("code")["c_price"].transform(lambda x: x.rolling(20).mean())
df["MA_200"] = df.groupby("code")["c_price"].transform(lambda x: x.rolling(200).mean())
df["MA_250"] = df.groupby("code")["c_price"].transform(lambda x: x.rolling(250).mean())

# 选股条件计算
df["SXHCG20"] = df["c_price"] > df["MA_20"]

df["SXHCG21"] = df.groupby("code")["c_price"].transform(
    lambda x: x.rolling(30).apply(lambda y: (y > df["MA_250"]).sum(), raw=True)
) >= 25

df["SXHCG22"] = df.groupby("code")["c_price"].transform(
    lambda x: x.rolling(30).apply(lambda y: (y > df["MA_200"]).sum(), raw=True)
) >= 25

df["SXHCG23"] = df.groupby("code")["c_price"].transform(
    lambda x: x.rolling(10).apply(lambda y: (y > df["MA_20"]).sum(), raw=True)
) >= 9

df["SXHCG24"] = df.groupby("code").apply(
    lambda x: ((x["c_price"] > x["MA_10"]) & (x["c_price"] > x["MA_20"]))
              .rolling(4)
              .sum()
              >= 3
).reset_index(level=0, drop=True)

# 最终选股条件
df["SXHCG2"] = df["SXHCG20"] & df["SXHCG21"] & df["SXHCG22"] & (df["SXHCG23"] | df["SXHCG24"])

# 过滤符合条件的股票
selected_stocks = df[df["SXHCG2"]][["code", "c_date", "c_price"]]

# 输出符合条件的股票
print(selected_stocks)
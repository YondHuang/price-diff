import pandas as pd
from data.DataBase import DataBase

"""
每日观察条件选股
"""

config_file = '../config.yml'
dataIns = DataBase(config_file)

#最近一天的记录时间是什么时候
conditions = {"num": 150}
data = dataIns.getCommonData('stock_extra_rank', ['c_date'], conditions, 'c_date desc', '1')
df = pd.DataFrame(data)
# print(df)
dateInfo = df.loc[0, 'c_date']
print(dateInfo)

pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列

#extra的150天排名
conditions = {"c_date": dateInfo, "num": 150}
data = dataIns.getCommonData('stock_extra_rank', ['code', 'extra_val', 'num', 'c_date', 'rank_val'], conditions, '', '')
df150 = pd.DataFrame(data)
print(df150)
# 将 rank_val 转为浮点数
df150['rank_val'] = df150['rank_val'].astype(float)

# 计算 rank_val 列的 85% 分位点（即前 15% 的阈值）
threshold = df150['rank_val'].quantile(0.85)
# 筛选出 rank_val 值大于等于分位点的数据
top20Percent150 = df150[df150['rank_val'] >= threshold]
print("df150", len(top20Percent150))
print(top20Percent150)


#extra的250天排名
conditions = {"c_date": dateInfo, "num": 250}
data = dataIns.getCommonData('stock_extra_rank', ['code', 'extra_val', 'num', 'c_date', 'rank_val'], conditions, '', '')
df250 = pd.DataFrame(data)
print(df250)
# 将 rank_val 转为浮点数
df250['rank_val'] = df250['rank_val'].astype(float)
# 计算 rank_val 列的 85% 分位点（即前 15% 的阈值）
threshold = df250['rank_val'].quantile(0.85)
# 筛选出 rank_val 值大于等于分位点的数据
top20Percent250 = df250[df250['rank_val'] >= threshold]
print("df250", len(top20Percent250))
print(top20Percent250)

rpsTop20Res = pd.concat([top20Percent150, top20Percent250], ignore_index=True)

#过去5天最高价格列表
data = dataIns.getDistinctCommonData('stock_record', ['c_date'], {}, 'c_date desc', '5')
df = pd.DataFrame(data)
inWhere = '(' + ','.join(f"'{date}'" for date in df['c_date']) + ')'
#print(inWhere)
data = dataIns.getCommonInData('stock_record', ['max(h_price) as hPrice', 'code'], True, 'c_date', inWhere, {}, 'code')
h5df = pd.DataFrame(data)
print(h5df)

for index, row in h5df.iterrows():
    conditions = {"code": row['code']}
    print(f"code {row['code']} in last 5 day high price:{row['hPrice']}")
    #过去250天最高价格列表
    data = dataIns.getDistinctCommonData('stock_record', ['c_date'], conditions, 'c_date desc', '250')
    df = pd.DataFrame(data)
    inWhere = '(' + ','.join(f"'{date}'" for date in df['c_date']) + ')'
    #print(inWhere)
    data = dataIns.getCommonInData('stock_record', ['max(h_price) as hPrice'], True, 'c_date', inWhere, conditions)
    print(data)
    # df = pd.DataFrame(data)
    print(f"in last 250 day high price:{data[0]['hPrice']}")
    if row['hPrice'] >= data[0]['hPrice']:
        print("5 day high price >=  250 day high price")
    else:
        print("5 day high price <  250 day high price")
        h5df.drop(index, inplace=True)
        #dataIns.saveCommonData("")

print("h5df")
print(h5df)

# 取交集
intersection = pd.merge(rpsTop20Res, h5df, on='code')
print(intersection)





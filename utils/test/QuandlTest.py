import requests
import pandas as pd
from data.DataBase import DataBase
import time
import quandl

# # 设置 Quandl API 密钥
quandl.ApiConfig.api_key = 'dd3y3J3XhJhUNtyVz8CK'

# 获取股票和 ETF 符号，排除加密货币
#url = f'https://api.polygon.io/v3/reference/tickers?apiKey={api_key}'

sina_config_file = '../../config.yml'
dataIns = DataBase(sina_config_file)

# 设置栈空间为 10 MB
#ctypes.windll.kernel32.SetThreadStackGuarantee(ctypes.c_ulong(10 * 1024 * 1024))

# 示例股票列表
# stock_symbols = [{'code': 'ACHR'},{'code': 'FI'}]
sql = "select DISTINCT code from stock_basic where is_closed=0 and code not in (SELECT code from stock_record where c_date='2025-02-06')"
stock_symbols = dataIns.getSqlData(sql)

symbols = [item['code'] for item in stock_symbols]

print(symbols)

## 写入数据库
fields = ['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']

start_date = "2025-02-06"
end_date = "2025-02-08"


for symbol in symbols:
    print(f"Fetching data for {symbol}...")
    data = quandl.get(f"EOD/{symbol}", start_date=start_date, end_date=end_date)

    print(data)
    # 如果需要查看数据的结构：
    print(data.head())
    print(data.head())

    # # 检查数据是否存在
    # if "results" in data:
    #     # 解析数据
    #     df = pd.DataFrame(data["results"])
    #
    #     # 转换时间戳为日期格式
    #     df["timestamp"] = pd.to_datetime(df["t"], unit='ms').dt.date
    #     df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume", "timestamp": "Date"}, inplace=True)
    #
    #     # 打印数据
    #     pd.set_option('display.max_columns', None)  # 显示所有列
    #     pd.set_option('display.width', 1000)        # 设置显示宽度
    #     print(df)
    #     df["code"] = symbol  # 添加 code 列
    #
    #     # 删除不需要的列
    #     df = df.drop(columns=["t", "n"])
    #
    #     # 将列名映射到数据库字段名
    #     #fields = ['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']
    #     column_mapping = {
    #         "Date": "c_date",
    #         "Open": "o_price",
    #         "High": "h_price",
    #         "Low": "l_price",
    #         "Close": "c_price",
    #         "Volume": "vol",
    #         "vw": "remark"
    #     }
    #     df.rename(columns=column_mapping, inplace=True)
    #     print(df)
    #
    #     df[['o_price', 'h_price', 'l_price', 'c_price']] = df[['o_price', 'h_price', 'l_price', 'c_price']].fillna(0)
    #     print(df)
    #
    #     # 转换为符合批量插入格式的 values
    #     values = df[['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']].values.tolist()
    #     print(values)
    #     print(values)
    #
    #     #dataIns.saveBatchCommonData('stock_record', fields, values)
    #     time.sleep(1.3)




from ib_insync import *
import pandas as pd
from data.DataBase import DataBase
import logging.config
import time


# 连接到 IB TWS 或 IB Gateway（请确保已启动 TWS/IB Gateway 并启用 API 访问）
ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)  # 7497 是纸交易端口，7496 是真实交易端口

# 加载配置文件
logging.config.fileConfig('../../logging.conf')

config_file = '../../config.yml'
dataIns = DataBase(config_file)

# 设置栈空间为 10 MB
#ctypes.windll.kernel32.SetThreadStackGuarantee(ctypes.c_ulong(10 * 1024 * 1024))

# 示例股票列表
# stock_symbols = [{'code': 'ACHR'},{'code': 'FI'}]
sql = "select DISTINCT code from stock_basic where is_closed=0 and code not in (SELECT code from stock_record where c_date='2025-02-06')"
stock_symbols = dataIns.getSqlData(sql)

symbols = [item['code'] for item in stock_symbols]

# symbols = {'HSIC'}
print(symbols)

## 写入数据库
fields = ['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']


for symbol in symbols:
    print(f"Fetching data for {symbol}...")
    # 定义 AAPL 股票合约
    contract = Stock(f"{symbol}", 'SMART', 'USD')

    # 设置查询结束时间（使用 UTC 格式，避免时区错误）
    end_time = '20250208-00:00:00'  # 2025年2月8日 00:00:00 UTC

    # 请求历史数据
    bars = ib.reqHistoricalData(
        contract,
        endDateTime=end_time,  # 修正格式
        durationStr='2 D',  # 查询过去 2 天数据
        barSizeSetting='1 day',  # 按日获取数据
        whatToShow='TRADES',  # 交易数据
        useRTH=True,  # 仅使用正常交易时间的数据
        formatDate=1
    )

    # print(bars)

    # 将 BarData 转换为 DataFrame
    df = pd.DataFrame([{
        "date": bar.date,
        "open": bar.open,
        "high": bar.high,
        "low": bar.low,
        "close": bar.close,
        "volume": bar.volume,
        "average": bar.average,
        "barCount": bar.barCount
    } for bar in bars])

    if df.empty:
        print(f"No data found for {symbol}. Skipping...")
        logging.error(f"No data found for {symbol}. Skipping...")
        continue

    df["code"] = symbol  # 添加 code 列
    print(df)

    # 删除不需要的列
    df = df.drop(columns=["barCount"])

    # 将列名映射到数据库字段名
    #fields = ['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']
    column_mapping = {
        "date": "c_date",
        "open": "o_price",
        "high": "h_price",
        "low": "l_price",
        "close": "c_price",
        "volume": "vol",
        "average": "remark"
    }
    df.rename(columns=column_mapping, inplace=True)
    print(df)

    df[['o_price', 'h_price', 'l_price', 'c_price']] = df[['o_price', 'h_price', 'l_price', 'c_price']].fillna(0)
    print(df)

    # 转换为符合批量插入格式的 values
    values = df[['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']].values.tolist()
    print(values)
    print(values)

    dataIns.saveBatchCommonData('stock_record', fields, values)
    time.sleep(1)

    # 打印数据
    # for bar in bars:
    #     print(f"Date: {bar.date}, Open: {bar.open}, High: {bar.high}, Low: {bar.low}, Close: {bar.close}, Volume: {bar.volume}")

# 断开连接
ib.disconnect()

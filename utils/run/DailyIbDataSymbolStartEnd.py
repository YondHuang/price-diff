from ib_insync import *
import pandas as pd
from data.DataBase import DataBase
import logging.config
from datetime import datetime, timedelta
import time
from decimal import Decimal, ROUND_DOWN


# 连接到 IB TWS 或 IB Gateway（请确保已启动 TWS/IB Gateway 并启用 API 访问）
ib = IB()
ib.connect('104.194.79.173', 4001, clientId=1, timeout=30)  # 7497 是纸交易端口，7496 是真实交易端口

# 加载配置文件
logging.config.fileConfig('../../logging.conf')

sina_config_file = '../../config.yml'
dataIns = DataBase(sina_config_file)

# 设置栈空间为 10 MB
#ctypes.windll.kernel32.SetThreadStackGuarantee(ctypes.c_ulong(10 * 1024 * 1024))

# 示例股票列表
# stock_symbols = [{'code': 'ACHR'},{'code': 'FI'}]
#sql = "select code from stock_basic where is_closed = 0 and code not in (select DISTINCT code from stock_record)"
# sql = "select code from stock_basic where code not in (select DISTINCT code from stock_record UNION SELECT code from no_data_stock)"
# sql = "select DISTINCT code from stock_basic"
sql = "select code from stock_basic where code not in (select DISTINCT code from stock_record where c_date='2025-02-20')"
stock_symbols = dataIns.getSqlData(sql)
symbols = [item['code'] for item in stock_symbols]

# symbols = {'ACON','ALLR','CRKN','MULN'}
print(symbols)

## 写入数据库
no_data_fields = ['code']
fields = ['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']

# 设置查询结束时间（使用 UTC 格式，避免时区错误）
current_datetime = datetime.utcnow().date()  # 获取当前日期部分
end_time = current_datetime.strftime('%Y%m%d-00:00:00')  # 格式化为指定格式
print(end_time)

# 假设 df 是你的 DataFrame
def convert_to_decimal(df, columns):
    """
    将指定列的数值转换为 Decimal 类型，保留四位小数

    :param df: 包含数据的 DataFrame
    :param columns: 需要转换的列名列表
    :return: 转换后的 DataFrame
    """
    for col in columns:
        # 转换列的每个值为 Decimal 类型并保留 4 位小数
        df[col] = df[col].apply(lambda x: Decimal(x).quantize(Decimal('0.0001'), rounding=ROUND_DOWN) if pd.notnull(x) else None)
    return df

for symbol in symbols:
    print(f"Fetching data for {symbol}...")
    # 定义 AAPL 股票合约
    contract = Stock(f"{symbol}", 'SMART', 'USD')

    # 请求历史数据
    bars = ib.reqHistoricalData(
        contract,
        endDateTime=end_time,  # 修正格式
        durationStr='1 D',  # 查询过去 2 天数据
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
        ##no_data_stock

        values = []
        stock_info = {
            "code": symbol
        }

        # print(stock_info)
        # 将每只股票的信息加入到values列表
        values.append(stock_info)
        dataIns.saveCommonData('no_data_stock', no_data_fields, values)
        continue

    df["code"] = symbol  # 添加 code 列
    # print(df)

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
    # print(df)

    df[['o_price', 'h_price', 'l_price', 'c_price']] = df[['o_price', 'h_price', 'l_price', 'c_price']].fillna(0)

    # 需要转换的列
    price_columns = ['o_price', 'h_price', 'l_price', 'c_price']

    # 转换 DataFrame 中的相关列
    df = convert_to_decimal(df, price_columns)
    # print(df)

    # 转换为符合批量插入格式的 values
    values = df[['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']].values.tolist()
    # print(values)

    dataIns.saveBatchCommonData('stock_record', fields, values)
    time.sleep(1)

    # 打印数据
    # for bar in bars:
    #     print(f"Date: {bar.date}, Open: {bar.open}, High: {bar.high}, Low: {bar.low}, Close: {bar.close}, Volume: {bar.volume}")

# 断开连接
ib.disconnect()

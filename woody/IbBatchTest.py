import asyncio
from ib_insync import *
import pandas as pd
from data.DataBase import DataBase
import logging.config
from datetime import datetime, timedelta
import time
from decimal import Decimal, ROUND_DOWN
import concurrent.futures
from functools import partial

# 连接到 IB TWS 或 IB Gateway
ib = IB()
ib.connect('104.194.79.173', 4001, clientId=1, timeout=30)

# 加载配置文件
logging.config.fileConfig('../logging.conf')
sina_config_file = '../config.yml'
dataIns = DataBase(sina_config_file)

# SQL 查询
sql = "select DISTINCT code from stock_basic"
stock_symbols = dataIns.getSqlData(sql)
symbols = [item['code'] for item in stock_symbols]
print(symbols)

# 数据库字段
no_data_fields = ['code']
fields = ['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']

# 设置查询结束时间
current_datetime = datetime.utcnow().date()
end_time = current_datetime.strftime('%Y%m%d-00:00:00')
print(end_time)

# Decimal 转换函数
def convert_to_decimal(df, columns):
    for col in columns:
        df[col] = df[col].apply(lambda x: Decimal(str(x)).quantize(Decimal('0.0001'), rounding=ROUND_DOWN) if pd.notnull(x) else None)
    return df

# 处理单个symbol的函数
def fetch_and_process_symbol(symbol, end_time, ib_instance, data_ins):
    # 在线程中设置事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        print(f"Fetching data for {symbol}...")
        contract = Stock(symbol, 'SMART', 'USD')

        # 请求历史数据
        bars = ib_instance.reqHistoricalData(
            contract,
            endDateTime=end_time,
            durationStr='5 D',
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )

        # 转换为 DataFrame
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
            values = [{"code": symbol}]
            data_ins.saveCommonData('no_data_stock', no_data_fields, values)
            return None

        df["code"] = symbol
        df = df.drop(columns=["barCount"])

        # 列名映射
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

        df[['o_price', 'h_price', 'l_price', 'c_price']] = df[['o_price', 'h_price', 'l_price', 'c_price']].fillna(0)

        price_columns = ['o_price', 'h_price', 'l_price', 'c_price']
        df = convert_to_decimal(df, price_columns)
        print(df)

        values = df[['code', 'c_date', 'o_price', 'h_price', 'l_price', 'c_price', 'vol', 'remark']].values.tolist()
        # data_ins.saveBatchCommonData('stock_record', fields, values)

        print(f"Completed processing {symbol}")
        return df

    except Exception as e:
        print(f"Error processing {symbol}: {str(e)}")
        logging.error(f"Error processing {symbol}: {str(e)}")
        return None
    finally:
        loop.close()  # 关闭事件循环

# 并行处理所有symbols
def fetch_all_symbols_parallel(symbols, end_time, ib_instance, data_ins, max_workers=10):
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        fetch_func = partial(fetch_and_process_symbol, end_time=end_time, ib_instance=ib_instance, data_ins=data_ins)
        future_to_symbol = {executor.submit(fetch_func, symbol): symbol for symbol in symbols}

        results = []
        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                df = future.result()
                if df is not None:
                    results.append(df)
            except Exception as e:
                print(f"Failed to process {symbol}: {str(e)}")
                logging.error(f"Failed to process {symbol}: {str(e)}")

    if results:
        final_df = pd.concat(results, ignore_index=True)
        print(f"Total execution time: {time.time() - start_time:.2f} seconds")
        return final_df
    return pd.DataFrame()

# 执行并行查询
result_df = fetch_all_symbols_parallel(symbols, end_time, ib, dataIns, max_workers=10)

# 断开连接
ib.disconnect()
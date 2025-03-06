import yfinance as yf
import numpy as np
import matplotlib
from ib_insync import Stock, IB
import time
from datetime import datetime, timedelta

matplotlib.use('TkAgg')  # 设置 Matplotlib 后端为 TkAgg
import pandas as pd
from data.DataBase import DataBase
import logging.config
import yaml

# 连接到 IB TWS 或 IB Gateway（请确保已启动 TWS/IB Gateway 并启用 API 访问）
ib = IB()
config_file = '../config.yml'

# 读取YAML配置文件
with open(config_file, 'r', encoding='utf-8', errors='ignore') as file:
    config = yaml.safe_load(file)
# 7497 是纸交易端口，7496 是真实交易端口
ib.connect(config['IBKR']['ip'], config['IBKR']['port'], clientId=1, timeout=30)


# 加载配置文件
logging.config.fileConfig('../logging.conf')

"""
查询指定名称的股票代码，把最近一天日期的价格数据都写入数据库stock_record
"""
dataIns = DataBase(config_file)

# 当前日期
current_date = datetime.now().date()

query_conditions = {"is_closed": 0}
stock_symbols = dataIns.getCommonData('stock_basic', ['code'], query_conditions, '', '')
# sql = f"select code from stock_basic where is_closed=0 and code not in (select code from notice_stock where c_date='2025-02-21')"
# stock_symbols = dataIns.getSqlData(sql)
symbols = [item['code'] for item in stock_symbols]


# symbols = {'SRCE','ETNB','ATEN','AIR','ABT'}
print(symbols)

## 写入数据库
no_data_fields = ['code']
fields = ['code', 'breakout_time', 'c_date']

# 获取股票数据
# stock = yf.Ticker("IBKR")
# # stock = yf.Ticker("UBER")
# # stock = yf.Ticker("META")
# # data = stock.history(period="3mo", interval="1d")
# data = stock.history(period="1y", interval="1d")

# 获取当前日期，时间设置为 00:00:00
current_datetime = datetime.utcnow().date()  # 获取当前日期部分
end_time = current_datetime.strftime('%Y%m%d-00:00:00')  # 格式化为指定格式
# end_time = '20250219-00:00:00'  # 2025年2月8日 00:00:00 UTC

for symbol in symbols:
    print(f"Fetching data for {symbol}, start at {datetime.now()}...")

    # 定义 AAPL 股票合约
    contract = Stock(f"{symbol}", 'SMART', 'USD')

    time.sleep(1)
    # 请求历史数据
    bars = ib.reqHistoricalData(
        contract,
        endDateTime=end_time,  # 修正格式
        durationStr='90 D',  # 查询过去 2 天数据
        barSizeSetting='1 day',  # 按日获取数据
        whatToShow='TRADES',  # 交易数据
        useRTH=True,  # 仅使用正常交易时间的数据
        formatDate=1
    )

    print(bars)

    # 将 BarData 转换为 DataFrame
    data = pd.DataFrame([{
        "date": bar.date,
        "open": bar.open,
        "high": bar.high,
        "low": bar.low,
        "Close": bar.close,
        "Volume": bar.volume,
        "average": bar.average,
        "barCount": bar.barCount
    } for bar in bars])

    if data.empty:
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

    # 将 date 列转换为索引
    data.set_index('date', inplace=True)
    data["code"] = symbol  # 添加 code 列
    # print(data)
    # 清理数据，移除NaN或Inf值
    data = data.dropna()
    data = data[np.isfinite(data['Close'])]

    # 计算SMA（简单移动平均）
    data['SMA50'] = data['Close'].rolling(window=50).mean()

    # 识别杯柄形态的突破点
    def identify_cup_handle_breakout(data, cup_up=0.015, cup_depth_threshold=0.06, handle_depth_threshold=0.08,
                                     volume_threshold=1.1, min_cup_days=13, min_dur_day = 3):
        """
        识别杯柄形态的突破点，自动确定杯子的开始和结束日期。
        :param data: 股票数据
        :param cup_depth_threshold: 杯子深度的阈值（百分比）
        :param handle_depth_threshold: 柄部深度的阈值（百分比）
        :param volume_threshold: 成交量放大倍数
        :param min_cup_days: 杯子至少要有多少个交易日的长度
        :return: 突破点的日期列表
        """
        breakout_points = []

        # 遍历整个数据寻找多个杯柄形态
        i = 0
        while i < len(data):
            # 寻找杯子的起始点
            cup_start = None
            cup_start_price = None
            cup_end = None
            cup_end_price = None
            cup_min = None

            # 遍历数据查找杯子的开始
            for j in range(i, len(data)):
                if j > 0 and data['Close'].iloc[j] < data['Close'].iloc[j-1]:
                    # 如果股价开始下跌，记录杯子的开始
                    if cup_start is None:
                        cup_start = data.index[j-1]
                        cup_start_price = data['Close'].iloc[j-1]
                    cup_min = min(cup_min, data['Close'].iloc[j]) if cup_min is not None else data['Close'].iloc[j]
                elif (cup_start is not None
                      and (data['Close'].iloc[j]) * (1 + cup_up) > data['Close'].iloc[j-1]
                      and (cup_start_price * (1 - cup_up) <= data['Close'].iloc[j] or cup_start_price <= data['Close'].iloc[j] <= cup_start_price * (1 + cup_up))):
                    # 如果股价开始上升，认为杯子的结束部分找到了
                    cup_end = data.index[j]
                    cup_end_price = data['Close'].iloc[j]
                    break

            # print(f"cup_start: {cup_start}")
            # print(f"cup_start_price: {cup_start_price}")
            # print(f"cup_min: {cup_min}")
            # print(f"cup_end: {cup_end}")
            # print(f"cup_end_price: {cup_end_price}")

            # 如果杯子的深度符合要求且持续时间足够
            if cup_start is not None and cup_end is not None:
                # 检查杯子深度是否满足阈值
                cup_depth = (data.loc[cup_start, 'Close'] - cup_min) / data.loc[cup_start, 'Close']
                cup_duration = (data.index.get_loc(cup_end) - data.index.get_loc(cup_start))
                if cup_depth >= cup_depth_threshold and cup_duration >= min_cup_days:
                    # 寻找柄部
                    handle_start = cup_end
                    handle_end = None
                    handle_min = None
                    for j in range(data.index.get_loc(handle_start), len(data)):
                        if data['Close'].iloc[j] < data['Close'].iloc[j-1]:
                            handle_min = min(handle_min, data['Close'].iloc[j]) if handle_min is not None else data['Close'].iloc[j]
                        elif handle_min is not None:
                            handle_end = data.index[j]
                            break

                    # 检查柄部深度是否满足阈值
                    if handle_start is not None and handle_end is not None:
                        handle_depth = (data.loc[handle_start, 'Close'] - handle_min) / data.loc[handle_start, 'Close']
                        if handle_depth <= handle_depth_threshold:

                            # 设置一个窗口，检查handle_end前后3天的数据
                            handle_end_loc = data.index.get_loc(handle_end)
                            start_range = max(handle_end_loc - min_dur_day, 0)  # 确保不超出数据的开始
                            end_range = min(handle_end_loc + min_dur_day, len(data) - 1)  # 确保不超出数据的结尾

                            # 寻找突破点
                            print(f"handle_end :{handle_end}")
                            for j in range(start_range, end_range + 1):
                                if (data['Close'].iloc[j] > data.loc[handle_start, 'Close']
                                        and data['Volume'].iloc[j] > volume_threshold * data['Volume'].iloc[j-1]
                                        and handle_end is not None):
                                    breakout_points.append(data.index[j])
                    # 更新扫描的位置，跳到下一个可能的杯形底部
                    i = data.index.get_loc(cup_end) + 1
                else:
                    i = data.index.get_loc(cup_end) + 1
            else:
                break  # 如果没有找到更多的杯子，结束循环

        return breakout_points

    # 识别突破点
    # pd.set_option('display.max_rows', None)  # 显示所有行
    # pd.set_option('display.max_columns', None)  # 显示所有列
    # pd.set_option('display.width', 1000)        # 设置显示宽度
    # print(data)
    min_dur_day = 3

    breakout_points = identify_cup_handle_breakout(data)
    if breakout_points:
        found = False  # 新增标记变量
        # 判断当前日期与 breakout_points 中每个日期的差值
        for breakout_date in breakout_points:
            if abs(current_date - breakout_date) <= timedelta(days=min_dur_day):
                found = True  # 标记有符合条件的日期
                # 创建一个空列表，用于存储所有股票的信息
                values = []
                # print(f"Breakout point within {min_dur_day} days: {breakout_date}")
                # print(f"breakout_points: {breakout_points}")
                # print(f"symbol: {symbol}")

                stock_info = {
                    "code": symbol,
                    "breakout_time": breakout_date,
                    "c_date": current_date
                }

                print(stock_info)
                # 将每只股票的信息加入到values列表
                values.append(stock_info)
                dataIns.saveCommonData('notice_stock', fields, values)
        # 循环结束后判断是否需要执行空操作
        if not found:  # 所有日期都不满足条件时
            values = []
            stock_info = {
                "code": symbol,
                "breakout_time": None,
                "c_date": current_date
            }
            values.append(stock_info)
            dataIns.saveCommonData('notice_stock', fields, values)
    else:
        # 创建一个空列表，用于存储所有股票的信息
        values = []
        stock_info = {
            "code": symbol,
            "breakout_time": None,
            "c_date": current_date
        }

        # print(stock_info)
        # 将每只股票的信息加入到values列表
        values.append(stock_info)
        dataIns.saveCommonData('notice_stock', fields, values)

    print(f"Fetching data for {symbol}, end at {datetime.now()}...")


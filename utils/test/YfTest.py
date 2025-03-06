import yfinance as yf
import sys
import os
import requests
import datetime
# 获取当前文件的上三级目录，即项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到 sys.path
if project_root not in sys.path:
    sys.path.append(project_root)

# 将 data 目录添加到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../data'))


from data.DataBase import DataBase

# # 获取 SPY ETF
# spy = yf.Ticker("SPY")
#
# # 获取 ETF 持仓信息（即成分股）
# holdings = spy.history(period="1d")
#
# # 打印持仓数据
# print(holdings)


import yfinance as yf
from utils.DateUtil import DateUtil

# 定义一个ticker列表
# tickers = [
#     #'ABMD',
#            'SLRN',
#            'ASTH',
#            'ATXS',
#            'BLDW',
#            'BRK.AQ',
#            'BRK.AX',
#            'BOC',
#            'VTOL',
#            #'BF.A',
#            'BY',
#            'CECO',
#            #'CINC',
#            #'CWEN.A',
#            'CBU',
#            'CON',
#            #'CNCE',
#            'CRD.AX',
#            'CRD.BK',
#            'DAY',
#            'DYN',
#            'ESI',
#            #'ERS-G',
#            'FSB',
#            'FBNC',
#            'FLG',
#            'FTRE',
#            'GAP',
#            #'GLIBA',
#            #'The',
#            'DOC',
#            'HEI-A',
#            'DINO',
#            'HHH',
#            'WLY',
#            'LLYVA',
#            #'FWON',
#            'LGF-A',
#            'MXCT',
#            'MTUS',
#            'MOG-A',
#            'NBBK',
#            'OBK',
#            'FNA',
#            'CNXN',
#            'MD',
#            'CATX',
#            'PFC',
#            'RBC',
#            'RGP',
#            'GEAR',
#            'SANA',
#            'SEAI',
#            'SEG',
#            'SOLV',
#            'SOUN',
#            #'SMTA',
#            'LRN',
#            #'STRCX',
#            'SUNN',
#            'SLVM',
#            'TBRG',
#            'DJT',
#            'UCB',
#            'PRKS',
#            #'USBGFS7',
#            'VNOM',
#            'WT']
tickers = ['CNR']


# 创建一个空列表，用于存储所有股票的信息
values = []

# 循环遍历每个ticker并获取相关信息
for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        print(info)

        dateIns = DateUtil()

        # 提取信息并收集到列表
        stock_info = {
            "code": info.get('symbol'),
            "name": info.get('longName'),
            "gics_sector": info.get('sector'),
            "gics_sub_industry": info.get('industry'),
            "address": info.get('address1'),
            "city": info.get('city'),
            "state": info.get('state'),
            "zip": info.get('zip'),
            "country": info.get('country'),
            "phone": info.get('phone'),
            "website": info.get('website'),
            "founded": dateIns.toMysqlDatetime(dateIns.safeTimestampToDate(info.get('firstTradeDateEpochUtc'))),
            "is_wilshire5000": 1
        }

        print(stock_info)
        # 将每只股票的信息加入到values列表
        values.append(stock_info)
    except requests.exceptions.HTTPError as e:
        # 如果是 404 错误，跳过并打印提示
        if e.response.status_code == 404:
            print(f"Data for ticker {ticker} not found (404). Skipping...")
        else:
            # 处理其他 HTTP 错误
            print(f"HTTPError for ticker {ticker}: {e}")
    except Exception as e:
        # 处理其他异常
        print(f"Error for ticker {ticker}: {e}")

    # 打印每个股票的基本信息
    # print(f"Symbol: {info.get('symbol')}")
    # print(f"Security: {info.get('longName')}")
    # print(f"GICS Sector: {info.get('sector')}")
    # print(f"GICS Sub-Industry: {info.get('industry')}")
    # print(f"Headquarters Location: {info.get('address1')}, {info.get('city')}")
    # print(f"Founded: {info.get('founded')}")
    # print("-" * 40)  # 分隔线


print(values)
config_file = '../../config.yml'
db = DataBase(config_file)
fields = ['code', 'name', 'gics_sector', 'gics_sub_industry', 'address', 'city', 'state', 'zip', 'country',
          'phone', 'website', 'founded', 'is_wilshire5000']


db.saveCommonData('stock_basic', fields, values)
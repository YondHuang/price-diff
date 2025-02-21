import yfinance as yf
import pandas as pd
import time
import logging.config

# 加载配置文件
logging.config.fileConfig('../../logging.conf')

yf.enable_debug_mode()

class YahooFin:
    def fetchData(self, symbol, period='1mo', interval='1d'):
        """
        从 Yahoo Finance 获取历史数据

        :param symbol: 股票符号
        :param period: 获取数据的时间范围 (e.g., '1mo', '3mo', '1y'),'1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
        :param interval: 数据间隔 ('1d', '1wk', '1mo')
        :return: 包含股票数据的 DataFrame
        """

        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)
        return df

    def fetchStartEndData(self, symbol, start=None, end=None, interval='1d'):
        """
        从 Yahoo Finance 获取历史数据

        :param symbol: 股票符号
        :param start: 开始日期 (格式: 'YYYY-MM-DD')
        :param end: 结束日期 (格式: 'YYYY-MM-DD')
        :param interval: 数据间隔 ('1d', '1wk', '1mo')
        :return: 包含股票数据的 DataFrame
        """
        try:
            stock = yf.Ticker(symbol)

            # 获取历史数据
            df = stock.history(start=start, end=end, interval=interval)

            # 检查返回的数据是否为空
            if df.empty:
                logging.warning(f"No data returned for {symbol} between {start} and {end}.")
                return pd.DataFrame()  # 返回空 DataFrame

            # 设置适当的列名和格式（根据需要可以自定义）
            df = df.reset_index()  # 重置索引，便于后续操作
            df["symbol"] = symbol  # 添加股票符号列，方便后续数据管理

            time.sleep(3)  # 避免发送过多请求，可以根据实际需求调整延迟时间

            return df

        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()  # 如果发生异常，返回空的 DataFrame
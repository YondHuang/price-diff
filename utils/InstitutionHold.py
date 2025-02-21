import yfinance as yf
import pandas as pd

class InstitutionHold:

    #机构投资者持股比例
    def checkInstitutionalPercentHeld(self, symbol, percent):
        # 获取股票数据
        stock = yf.Ticker(symbol)
        holders = stock.major_holders

        # 输出前几位股东的持股比例（通常包括机构股东）
        # insidersPercentHeld：内部人员（如高管）持股比例。
        # institutionsPercentHeld：机构投资者持股比例。
        # institutionsFloatPercentHeld：流通股中被机构持有的比例。
        # institutionsCount：机构投资者的数量，共有多少个机构投资者持有该股票。
        # print("Institutional holders:")
        # print(holders)

        # 确保 holders 是 DataFrame
        if isinstance(holders, pd.DataFrame):
            # 获取机构持股比例
            institutions_percent_held = holders.loc['institutionsPercentHeld', 'Value'] if 'institutionsPercentHeld' in holders.index else 0
        else:
            institutions_percent_held = 0

        # 筛选条件：机构持股比例 > percent%
        if institutions_percent_held > percent:
            return True
        return False

    #流通股中被机构持有的比例
    def checkInstitutionalFloatPercentHeld(self, symbol, percent):
        # 获取股票数据
        stock = yf.Ticker(symbol)
        holders = stock.major_holders

        # 输出前几位股东的持股比例（通常包括机构股东）
        # insidersPercentHeld：内部人员（如高管）持股比例。
        # institutionsPercentHeld：机构投资者持股比例。
        # institutionsFloatPercentHeld：流通股中被机构持有的比例。
        # institutionsCount：机构投资者的数量，共有多少个机构投资者持有该股票。
        # print("Institutional holders:")
        # print(holders)

        # 确保 holders 是 DataFrame
        if isinstance(holders, pd.DataFrame):
            # 流通股中被机构持有的比例
            institutions_float_percent_held = holders.loc['institutionsFloatPercentHeld', 'Value'] if 'institutionsFloatPercentHeld' in holders.index else 0
        else:
            institutions_float_percent_held = 0

        # 筛选条件：流通股中被机构持有的比例 > percent%
        if institutions_float_percent_held > percent:
            return True
        return False

    #机构投资者的数量，共有多少个机构投资者持有该股票
    def checkInstitutionalCount(self, symbol, min, max):
        # 获取股票数据
        stock = yf.Ticker(symbol)
        holders = stock.major_holders

        # 输出前几位股东的持股比例（通常包括机构股东）
        # insidersPercentHeld：内部人员（如高管）持股比例。
        # institutionsPercentHeld：机构投资者持股比例。
        # institutionsFloatPercentHeld：流通股中被机构持有的比例。
        # institutionsCount：机构投资者的数量，共有多少个机构投资者持有该股票。
        # print("Institutional holders:")
        # print(holders)

        # 确保 holders 是 DataFrame
        if isinstance(holders, pd.DataFrame):
            # 机构投资者的数量
            institutions_count = holders.loc['institutionsCount', 'Value'] if 'institutionsCount' in holders.index else 0
        else:
            institutions_count = 0

        # 筛选条件：min <= 机构投资者的数量 并且 机构投资者的数量 <= max
        if min <= institutions_count and institutions_count <= max:
            return True
        return False
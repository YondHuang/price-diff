import pandas as pd
from plugins.YahooFin import YahooFin
from decimal import Decimal
import numpy as np

from sklearn.preprocessing import MinMaxScaler

class ExtrsUtil:

    def extrs(self, df, N):
        """
        计算通达信公式 EXTRS: (C - REF(C, N)) / REF(C, N)

        :param df: 包含收盘价的 pandas DataFrame
        :param N: N 日的周期数
        :return: 计算后的相对变化率
        """
        # 如果 df 是列表类型，先将其转换为 DataFrame
        if isinstance(df, list):
            df = pd.DataFrame(df)

        # 确保按 'c_date' 排序
        df = df.sort_values(by='c_date')

        # 将 'c_price' 转换为浮动数值（如果是 Decimal 类型）
        df['c_price'] = df['c_price'].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

        df['num'] = N

        # pd.set_option('display.max_rows', None)  # 显示所有行
        # pd.set_option('display.max_columns', None)  # 显示所有列
        # pd.set_option('display.width', 1000)        # 设置显示宽度
        # print(df)

        # 计算 N 天前的收盘价，使用 shift(N) 来获取 N 天前的 'c_price'
        df['ref_c'] = df['c_price'].shift(N)

        # 防止除以 0 或无效值，将 ref_c 中的 0 替换为 NaN
        df['ref_c'] = df['ref_c'].replace(0, np.nan)

        # 计算 EXTRS (相对变化率)
        df['extra_val'] = (df['c_price'] - df['ref_c']) / df['ref_c']

        # 去除 NaN 值，确保 EXTRS 列是有效的
        df = df.dropna(subset=['extra_val'])

        return df

    # def extrsRank(self, data):
    #     """
    #     根据 DataFrame 中的 extra_val (涨幅) 计算排名 rank_val。
    #     涨幅最小值（可能为负数）对应 rank_val 为 0；
    #     涨幅最大值对应 rank_val 为 100；
    #     其他值按涨幅比例映射到 0-100 之间。
    #     """
    #     df = data.copy()
    #
    #     # 确保 extra_val 是浮点数
    #     df['extra_val'] = df['extra_val'].astype(float)
    #
    #     # 获取涨幅的最小值和最大值
    #     min_val = df['extra_val'].min()
    #     max_val = df['extra_val'].max()
    #     print(f"min_val: {min_val}, max_val: {max_val}")
    #
    #     # 定义一个函数，根据 extra_val 的值计算 rank_val
    #     def calculate_rank(val):
    #         if max_val == min_val:
    #             # 如果所有值相等，直接将 rank_val 设置为 100
    #             return 100
    #         return 100 * (val - min_val) / (max_val - min_val)
    #
    #     # 应用函数计算 rank_val
    #     df['rank_val'] = df['extra_val'].apply(calculate_rank)
    #
    #     return df

    def extrsRank(self, data):
        """
        对 DataFrame 中的 extra_val 字段计算中位数，并根据值与中位数的关系赋值 rank_val。
        rank_val 的范围是从 1 到 99。
        最小的涨幅设置成 1，按照涨幅设置 rank_val 从 1-100 之间，注意不包括 100。
        """
        df = data.copy()

        # 使用 RANK 方法
        df['rank'] = df['extra_val'].rank(method='max')

        # 使用 PCTRANK 方法
        df['rank_val'] = df['extra_val'].rank(method='max', pct=True) * 100

        return df

    def extrsRank1(self, data):
        """
        对 DataFrame 中的 extra_val 字段计算中位数，并根据值与中位数的关系赋值 rank_val。
        rank_val 的范围是从 0 到 100，大于中位数的值会被赋予大于 50 的排名。
        """
        df = data.copy()

        # 计算 extra_val 的中位数
        median_val = df['extra_val'].median()
        print(f"median_val:{median_val}")

        df['extra_val'] = df['extra_val'].astype(float)

        # 定义一个函数，根据 extra_val 的值计算 rank_val
        def calculate_rank(val):
            if val > median_val:
                # 如果值大于中位数，rank_val 在 50 到 100 之间
                if df['extra_val'].max() == median_val:
                    return 100  # 如果最大值等于中位数，直接赋值为100
                return 50 + (val - median_val) / (df['extra_val'].max() - median_val) * 50
            else:
                # 如果值小于等于中位数，rank_val 在 0 到 50 之间
                if df['extra_val'].min() == median_val:
                    return 0 if val == df['extra_val'].min() else 50  # 如果最小值等于中位数，直接赋值为0
                return 50 * (val - df['extra_val'].min()) / (median_val - df['extra_val'].min())

        # 应用函数计算 rank_val
        df['rank_val'] = df['extra_val'].apply(calculate_rank)

        return df
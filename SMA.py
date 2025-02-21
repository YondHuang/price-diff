
class Sma:
    def calculate_sma(prices, n):
        """
        计算简单移动平均线(SMA)

        参数:
        prices (list): 包含历史收盘价的列表，长度至少为n。
        n (int): 要计算的SMA的周期（如5日线）。

        返回:
        float: 计算出的SMA值。
        """
        if len(prices) < n:
            raise ValueError(f"历史价格数据不足，至少需要 {n} 个数据")

        # 求前n-1天的收盘价和
        sum_prev_n_minus_1 = sum(prices[-(n-1):])

        # 计算不动点SMA
        sma = sum_prev_n_minus_1 / (n - 1)

        return sma


# 示例使用
# 假设这是最近5天的收盘价列表
#prices = [31.50, 32.00, 31.80, 32.10, 32.20]  # X0, X1, X2, X3, X4
prices = [0.746, 0.748, 0.731, 0.727, 0.755]  # X0, X1, X2, X3, X4
n = 5

sma = Sma.calculate_sma(prices, n)
print(f"5日均线: {sma}")

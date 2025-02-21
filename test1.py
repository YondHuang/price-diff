def calculate_nav(xop_price, sps_op_current, sps_op_previous, hf_cl_price, usd_cny_previous, usd_cny_current, previous_nav_cny):
    """
    计算华宝油气净值（人民币）
    :param xop_price: XOP 最新价
    :param sps_op_current: 当前标普油气指数点数
    :param sps_op_previous: 昨日标普油气指数点数
    :param hf_cl_price: WTI 原油期货价格
    :param usd_cny_previous: 昨日美元兑人民币汇率
    :param usd_cny_current: 当前美元兑人民币汇率
    :param previous_nav_cny: 华宝油气昨日人民币净值
    :return: 估算的人民币净值
    """
    # Calculate SPSIOP percentage change
    sps_op_change = (sps_op_current - sps_op_previous) / sps_op_previous

    # Calculate WTI oil price factor
    wti_factor = hf_cl_price / sps_op_current

    # Calculate XOP factor
    xop_factor = xop_price / sps_op_current

    # Calculate USD/CNY change factor
    usd_cny_change = usd_cny_current / usd_cny_previous

    # Calculate the new net asset value (NAV) in CNY
    new_nav_cny = previous_nav_cny * (sps_op_change * wti_factor * xop_factor * usd_cny_change)

    return new_nav_cny

# 主程序
if __name__ == "__main__":
    xop_price = 128.33  # XOP 最新价
    sps_op_previous = 126.8100  # 昨日标普油气指数点数
    sps_op_current = 128.3300   # 当前标普油气指数点数
    hf_cl_price = 70.196  # WTI 原油期货价格
    usd_cny_previous = 7.2884  # 昨日美元兑人民币汇率
    usd_cny_current = 7.2980   # 当前美元兑人民币汇率
    previous_nav_cny = 0.7184   # 昨日人民币净值

    # Calculate SPSIOP percentage change
    sps_op_change = (sps_op_current - sps_op_previous) / sps_op_previous

    # Calculate WTI oil price factor
    wti_factor = hf_cl_price / sps_op_current

    # Calculate XOP factor
    xop_factor = xop_price / sps_op_current

    # Calculate USD/CNY change factor
    usd_cny_change = usd_cny_current / usd_cny_previous

    # Calculate the new net asset value (NAV) in CNY
    new_nav_cny = previous_nav_cny * (sps_op_change * wti_factor * xop_factor * usd_cny_change)

    # Print result
    print(f"Calculated Net Asset Value (CNY): {new_nav_cny:.4f}")


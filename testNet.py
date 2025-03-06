from plugins.Sina import Sina
from utils.StringUtil import StringUtil

code = 'sh600519'
code = 'gb_xop'
code = 'f_162411'

# config_file = 'config.yml'
# sina_instance = Sina(config_file)
# data = sina_instance.getStockData(code)
#
# db = DataBase(Sina.config_file)
# db.saveNetData(code, data)

# 获取新浪实时价格数据的函数
def get_sina_price(symbol):
    """
    获取新浪实时价格数据
    :param symbol: 新浪接口中的标识符，如 "gb_xop", "USDCNY"
    :return: 返回实时价格
    """

    config_file = 'config.yml'
    sina_instance = Sina(config_file)
    data = sina_instance.getStockData(symbol)
    print(data)

    str_instance = StringUtil()
    res = str_instance.strToArr(data)
    print(res)
    print(res[1])


    if "gb_" in symbol:  # 美股价格接口
        return float(res[1])  # 返回最新价格
    elif "hf_" in symbol:  # 商品期货接口
        return float(res[0])  # 返回最新价格
    elif "sz" in symbol or "sh" in symbol:  # A股或基金接口
        return float(res[3])  # 返回最新成交价
    elif symbol == "USDCNY":  # 汇率接口
        return float(res[8])  # 返回汇率
    else:
        return None

# 净值计算函数
# 净值计算函数（考虑人民币净值转换）
def calculate_nav_from_cny(previous_nav_cny, usdcny_previous, usdcny_current, xop_price, sps_op_current, sps_op_previous):
    """
    计算华宝油气净值（从人民币净值计算）
    :param previous_nav_cny: 昨日人民币净值
    :param usdcny_previous: 昨日美元兑人民币汇率
    :param usdcny_current: 今日美元兑人民币汇率
    :param xop_price: XOP 最新价
    :param sps_op_current: 当前标普油气指数点数
    :param sps_op_previous: 昨日标普油气指数点数
    :return: 估算的人民币净值
    """
    # 1. 人民币净值转换为美元净值
    previous_nav_usd = previous_nav_cny / usdcny_previous

    # 2. 计算美元计价净值
    benchmark_ratio = xop_price / sps_op_previous
    current_index = sps_op_current * benchmark_ratio
    current_nav_usd = previous_nav_usd * (current_index / sps_op_previous)

    # 3. 将美元净值转换为人民币
    current_nav_cny = current_nav_usd * usdcny_current

    return current_nav_cny

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
    # 1. 计算基准比率
    benchmark_ratio = xop_price / sps_op_previous

    # 2. 计算当前基准指数
    current_index = sps_op_current * benchmark_ratio

    # 3. 调整原油期货价格的影响
    adjusted_index = current_index * (hf_cl_price / 100)

    # 4. 将人民币净值转换为美元净值
    previous_nav_usd = previous_nav_cny / usd_cny_previous

    # 5. 计算当前美元净值
    current_nav_usd = previous_nav_usd * (adjusted_index / sps_op_previous)

    # 6. 将美元净值转换为人民币净值
    current_nav_cny = current_nav_usd * usd_cny_current

    return current_nav_cny


# 主程序
# Step 1: 获取实时数据
symbols = {
    "XOP": "gb_xop",  # XOP 美股 ETF
    "CL": "hf_CL",  # CL 纽约原油
    "SPS_OP": "标普油气指数",  # 替换成实际接口
    "USDCNY": "USDCNY",  # 美元兑人民币汇率
}

try:
    # 实时数据获取
    xop_price = get_sina_price(symbols["XOP"])
    #xop_price = 128.33
    #usd_cny_rate = get_sina_price(symbols["USDCNY"])
    usd_cny_current = get_sina_price(symbols["USDCNY"])
    #usd_cny_current = 7.298

    hf_cl_price = get_sina_price(symbols["CL"])

    # 手动设置 SPSIOP 的数据（需获取实际数据或设置固定值）
    sps_op_previous = 126.81  # 标普油气指数昨日点数
    sps_op_current = 128.330   # 标普油气指数当前点数

    usd_cny_previous = 7.2884  # 昨日美元兑人民币汇率

    # sps_op_previous = sps_op_previous / usd_cny_previous
    # sps_op_current = sps_op_current / usd_cny_previous
    # 华宝油气昨日美元净值（从官网查找）
    previous_nav_cny = 0.7184  # 手动设定为0.8（仅为示例）

    # Step 2: 计算净值
    #nav_cny = calculate_nav_from_cny(previous_nav_cny, usd_cny_previous, usd_cny_current, xop_price, sps_op_current, sps_op_previous)

    # Step 2: 计算净值
    #nav_cny = calculate_nav(xop_price, sps_op_current, sps_op_previous, hf_cl_price, sps_op_current, usd_cny_previous)
    nav_cny = calculate_nav(xop_price, sps_op_current, sps_op_previous, hf_cl_price, usd_cny_previous, usd_cny_current, previous_nav_cny)

    # 输出结果
    print(f"华宝油气估算净值（人民币）：{nav_cny:.4f}")

except Exception as e:
    print(f"数据获取或计算出错: {e}")
import requests
from bs4 import BeautifulSoup
import logging.config
from data.DataBase import DataBase

# 加载配置文件
logging.config.fileConfig('../logging.conf')

sina_config_file = '../config.yml'
dataIns = DataBase(sina_config_file)


# 请求URL模板，page 参数会在循环中动态替换
url_template = "https://api.stockanalysis.com/api/screener/s/f?m=marketCap&s=desc&c=no,s,n,marketCap,price,change,revenue&cn=1000&f=exchange-is-NYSE&p={page}&i=stocks"



# 设置请求头，包含你提供的 headers 信息
headers = {
    "Accept": "*/*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://stockanalysis.com",
    "Referer": "https://stockanalysis.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
}

# 创建一个空列表存储所有的股票数据
stock_data = []

# 最大页数为203
for page in range(1, 3):  # 页数从1到3
    # 构造URL
    url = url_template.format(page=page)
    print(f"url:{url}")

    # 发送请求并获取响应
    response = requests.get(url, headers=headers)

    # 确保请求成功
    if response.status_code == 200:
        data = response.json()  # 直接将响应内容转换为 JSON 格式

        print(data)  # 打印出data["data"]的内容，查看其结构

        # 提取每页的股票名称和股票代码
        for stock in data["data"]["data"]:  # 确保使用 "data" 这个键
            stock_data.append({
                "name": stock["n"],  # 股票名称
                "code": stock["s"]   # 股票代码
            })

        print(f"成功获取第{page}页数据")
        # print(stock_data)
    else:
        print(f"请求第{page}页失败，状态码: {response.status_code}")

# 输出所有股票的数据
print(f"stock_data:{stock_data}")

values = []
fields = ['code', 'name']
for stock in stock_data:
    # 构造符合数据库字段的记录
    values.append([
        stock['code'],         # 'code'
        stock['name']         # 'name'
    ])

print(values)
dataIns.saveBatchCommonData('nyse_stock', fields, values)

import requests
from bs4 import BeautifulSoup
import pandas as pd

# 获取 S&P 500 成分股的 Wikipedia 页面
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
response = requests.get(url)

# 使用 BeautifulSoup 解析网页
soup = BeautifulSoup(response.text, 'html.parser')

# 获取表格中的所有行
table = soup.find('table', {'class': 'wikitable'})

# 提取表格头部和数据行
headers = [header.text.strip() for header in table.find_all('th')]
rows = table.find_all('tr')

# 提取每一行的内容
data = []
for row in rows[1:]:
    cols = row.find_all('td')
    if len(cols) > 1:  # 排除空行
        data.append([col.text.strip() for col in cols])

# 将数据保存到 DataFrame 中
df = pd.DataFrame(data, columns=headers)

# 打印 DataFrame
# 设置显示最大行数和列数
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)  # 自动调整宽度，避免过长的行被折叠
pd.set_option('display.max_colwidth', None)  # 设置列宽，以防止内容被截断

# 打印 DataFrame
print(df)

# 如果你想保存为 CSV 文件，可以使用以下代码：
# df.to_csv("sp500_companies.csv", index=False)

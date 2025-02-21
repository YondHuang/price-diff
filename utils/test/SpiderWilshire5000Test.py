import requests
from bs4 import BeautifulSoup
import pandas as pd

# Wikipedia URL
url = "https://en.wikipedia.org/wiki/Wilshire_5000_Total_Market_Index"

# 发送请求并获取网页内容
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', {'class': 'wikitable'})

# 查找包含成分股的表格
# Wikipedia 页面上的成分股表格通常位于该页面的某个部分，包含股票代码、公司名称等信息
headers = [header.text.strip() for header in table.find_all('th')]
table = soup.find('table', {'class': 'wikitable'})

# 提取表格内容
columns = []
rows = []
for row in table.find_all('tr'):
    cells = row.find_all('td')
    if len(cells) > 0:
        # 提取每行的数据
        data = [cell.text.strip() for cell in cells]
        rows.append(data)

# 将提取的数据转换为 DataFrame
#df = pd.DataFrame(rows, columns=["Symbol", "Security", "GICS Sector", "GICS Sub-Industry", "Headquarters Location", "Date added", "CIK", "Founded"])
# 将数据保存到 DataFrame 中
df = pd.DataFrame(data, columns=headers)

# 设置显示最大行数和列数
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)  # 自动调整宽度，避免过长的行被折叠
pd.set_option('display.max_colwidth', None)  # 设置列宽，以防止内容被截断
# 显示前几行数据
print(df)

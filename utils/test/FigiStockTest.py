import requests
import jsonView  # 引入 json 库，用于捕获 JSONDecodeError

# 设置 Figi API 端点
url = "https://api.openfigi.com/v3/mapping"

# 请求头
headers = {
    'Content-Type': 'application/json',
    'X-OPENFIGI-APIKEY': '21735960-703d-48d3-bd5a-7d123119d796',
}

# 输入 ISIN
#isin = "US0378331005"  # 例如：Apple 的 ISIN
isin = "US088579Y101"  # 例如：Apple 的 ISIN   88579Y101

# 请求体
data = [{
    "idType": "ID_ISIN",
    "idValue": isin
}]

# 发送 POST 请求
response = requests.post(url, json=data, headers=headers)
print(response)

# 处理响应
if response.status_code == 200:
    figi_data = response.json()
    print(figi_data)
    if figi_data:
        figi = figi_data[0]['data'][0]
        print(f"Symbol: {figi['ticker']}")
        print(f"Name: {figi['name']}")
        print(f"Exchange: {figi['exchCode']}")
        print(f"Country: {figi['country']}")
    else:
        print("No data found.")
else:
    print("Request failed:", response.status_code, response.text)

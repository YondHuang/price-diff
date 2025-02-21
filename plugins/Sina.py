import requests
import yaml
import chardet


class Sina:

    config_file = '../config.yml'

    def __init__(self, config_file):
        # 读取YAML配置文件
        with open(config_file, 'r', encoding='utf-8', errors='ignore') as file:
            config = yaml.safe_load(file)

        # 从配置文件中提取数据库配置
        self.header = config['sina']['header']
        self.baseUrl = config['sina']['baseUrl']

    def getStockData(self, code):
        # 新浪股票实时数据API接口
        url = self.baseUrl + code  # 上证贵州茅台的股票代码是600519
        headers = {
            'Referer': self.header
        }

        response = requests.get(url, headers=headers)
        encoding = chardet.detect(response.content)['encoding']
        response.encoding = 'GBK'  # 使用检测到的编码
        if response.status_code == 200:
            data = response.text
            print(data)
            return data

        else:
            print("请求失败，状态码：", response.status_code)
            return None

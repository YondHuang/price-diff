from plugins.Sina import Sina
from data.DataBase import DataBase

code = 'sh600519'
code = 'gb_xop'
code = 'sz162411'

config_file = 'config.yml'
sina_instance = Sina(config_file)
data = sina_instance.getStockData(code)

db = DataBase(Sina.config_file)
db.saveRecordData(code, data)

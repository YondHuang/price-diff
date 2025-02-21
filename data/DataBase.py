# data/DataBase.py

import yaml
import pymysql

from utils.StringUtil import StringUtil


class DataBase:
    # 定义常量
    # 股票记录表
    STOCK_RECORD_TABLE = 'stock_record'
    # 净值表
    STOCK_NET_VALUE_TABLE = 'stock_net_val'

    def __init__(self, config_file):
        # 读取YAML配置文件
        with open(config_file, 'r', encoding='utf-8', errors='ignore') as file:
            config = yaml.safe_load(file)

        # 从配置文件中提取数据库配置
        self.host = config['database']['host']
        self.port = config['database']['port']
        self.user = config['database']['user']
        self.password = config['database']['password']
        self.dbName = config['database']['dbName']

        self.db_config = {
            'host': self.host,  # 数据库地址
            'user': self.user,  # 数据库用户名
            'password': self.password,  # 数据库密码
            'database': self.dbName,  # 数据库名称
            'port': self.port,  # 数据库端口，默认是 3306
            'charset': 'utf8mb4',  # 数据库字符集（默认是 utf8mb4）
            'autocommit': False,  # 是否自动提交事务（默认是 False）
            'cursorclass': pymysql.cursors.DictCursor,  # 设置游标类型
            'connect_timeout': 10  # 连接超时时间（默认10秒）
        }

    def saveRecordData(self, sCode, data):
        str_instance = StringUtil()
        try:
            # 创建数据库连接
            connection = pymysql.connect(**self.db_config)
            cursor = connection.cursor()
            # 插入数据的 SQL 语句
            sql = f"""
            INSERT INTO {DataBase.STOCK_RECORD_TABLE} (code, s_code, name, o_price, pc_price, price, h_price, l_price, 
            b_price, s_price, vol, amount, b1_num, b1_price, b2_num, b2_price, b3_num, b3_price, b4_num, b4_price, 
            b5_num, b5_price, s1_num, s1_price, s2_num, s2_price, s3_num, s3_price, s4_num, s4_price, s5_num, s5_price, 
            c_date, c_time, remark, date_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            res = str_instance.strToArr(data)
            # 在第一个元素前插入 -1
            res.insert(0, sCode)
            code = sCode[2:]  # 从索引 2 开始截取
            res.insert(0, code)
            # 获取倒数第三个和倒数第二个元素
            element = str(res[-3]) + ' ' + str(res[-2])  # 拼接为字符串
            res.append(element)
            print(res)

            # 执行插入操作
            cursor.execute(sql, res)
            connection.commit()  # 提交事务
        except pymysql.MySQLError as e:
            print(f"数据库操作失败：{e}")
            connection.rollback()  # 发生错误时回滚事务
        finally:
            # 关闭连接
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def saveCommonData(self, table, fields, values):
        str_instance = StringUtil()
        # 用逗号拼接成字符串
        fields_string = ", ".join(fields)
        # 根据字段数量生成对应数量的 %s
        placeholders = ", ".join(["%s"] * len(fields))
        try:
            # 创建数据库连接
            connection = pymysql.connect(**self.db_config)
            cursor = connection.cursor()
            # 插入数据的 SQL 语句
            sql = f"""
            INSERT INTO {table} ({fields_string})
            VALUES ({placeholders})
            """

            # 处理字典数据，将字典转为元组格式
            data_tuple = [
                tuple(d[field] for field in fields)  # 根据字段顺序从字典中提取数据
                for d in values
            ]

            for row in data_tuple:
                print(row)

            # print(sql, data_tuple)
            # 执行插入操作
            cursor.executemany(sql, data_tuple)
            connection.commit()  # 提交事务
            print(f"成功插入 {cursor.rowcount} 行数据到表 {table} 中。")
        except pymysql.MySQLError as e:
            print(f"数据库操作失败：{e}")
            connection.rollback()  # 发生错误时回滚事务
        finally:
            # 关闭连接
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def getCommonData(self, table, fields, conditions, orderByFields, limit):
        """
        从数据库中获取通用数据。

        :param table: 表名 (str)
        :param fields: 要查询的字段 (list or str)
        :param conditions: 查询条件 (dict)，键为字段名，值为字段值
        :return: 查询结果 (list of dicts)
        """
        # 创建数据库连接
        connection = pymysql.connect(**self.db_config)
        cursor = connection.cursor()
        # 处理字段部分
        if isinstance(fields, list):
            fields_string = ", ".join(fields)
        else:
            fields_string = fields

        # 构造条件部分
        where_clauses = []
        values = []
        for key, value in conditions.items():
            if isinstance(value, tuple):  # 处理带操作符的条件（如 <=, >=, != 等）
                operator, val = value
                where_clauses.append(f"{key} {operator} %s")
                values.append(val)
            else:  # 处理等于条件
                where_clauses.append(f"{key} = %s")
                values.append(value)
        where_clause = " AND ".join(where_clauses)

        # 构造 SQL 查询
        query = f"SELECT {fields_string} FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        if orderByFields:
            query += f" ORDER BY {orderByFields}"
        if limit:
            query += f" LIMIT {limit}"

        try:
            # 执行查询
            print(query, values)
            cursor.execute(query, values)
            results = cursor.fetchall()
            return results
        except pymysql.MySQLError as e:
            print(f"数据库操作失败：{e}")
            connection.rollback()  # 发生错误时回滚事务
        finally:
            # 关闭连接
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def getSqlData(self, sql):
        """
        从数据库中获取通用数据。

        :param table: 表名 (str)
        :param fields: 要查询的字段 (list or str)
        :param conditions: 查询条件 (dict)，键为字段名，值为字段值
        :return: 查询结果 (list of dicts)
        """
        # 创建数据库连接
        connection = pymysql.connect(**self.db_config)
        cursor = connection.cursor()

        try:
            # 执行查询
            print(sql)
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
        except pymysql.MySQLError as e:
            print(f"数据库操作失败：{e}")
            connection.rollback()  # 发生错误时回滚事务
        finally:
            # 关闭连接
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def getDistinctCommonData(self, table, fields, conditions, orderByFields, limit):
        """
        从数据库中获取通用数据。

        :param table: 表名 (str)
        :param fields: 要查询的字段 (list or str)
        :param conditions: 查询条件 (dict)，键为字段名，值为字段值
        :return: 查询结果 (list of dicts)
        """
        # 创建数据库连接
        connection = pymysql.connect(**self.db_config)
        cursor = connection.cursor()
        # 处理字段部分
        if isinstance(fields, list):
            fields_string = ", ".join(fields)
        else:
            fields_string = fields

        # 构造条件部分
        where_clauses = []
        values = []
        for key, value in conditions.items():
            where_clauses.append(f"{key} = %s")
            values.append(value)
        where_clause = " AND ".join(where_clauses)

        # 构造 SQL 查询
        query = f"SELECT DISTINCT {fields_string} FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        if orderByFields:
            query += f" ORDER BY {orderByFields}"
        if limit:
            query += f" LIMIT {limit}"

        try:
            # 执行查询
            print(query, values)
            cursor.execute(query, values)
            results = cursor.fetchall()
            return results
        except pymysql.MySQLError as e:
            print(f"数据库操作失败：{e}")
            connection.rollback()  # 发生错误时回滚事务
        finally:
            # 关闭连接
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def getCommonInData(self, table, fields, inFlag, inFiled, inWhere, conditions, groups=None):
        """
        从数据库中获取通用数据。

        :param table: 表名 (str)
        :param fields: 要查询的字段 (list or str)
        :param conditions: 查询条件 (dict)，键为字段名，值为字段值
        :return: 查询结果 (list of dicts)
        """
        # 创建数据库连接
        connection = pymysql.connect(**self.db_config)
        cursor = connection.cursor()
        # 处理字段部分
        if isinstance(fields, list):
            fields_string = ", ".join(fields)
        else:
            fields_string = fields

        # 构造条件部分
        where_clauses = []
        values = []
        for key, value in conditions.items():
            where_clauses.append(f"{key} = %s")
            values.append(value)
        where_clause = " AND ".join(where_clauses)

        # 构造 SQL 查询
        if inFlag:
            query = f"SELECT {fields_string} FROM {table} WHERE {inFiled} IN {inWhere}"
        else:
            query = f"SELECT {fields_string} FROM {table} WHERE {inFiled} NOT IN {inWhere}"
        if where_clause:
            query += " AND "
            query += f" {where_clause}"
        if groups:
            query += f" group by {groups}"

        try:
            # 执行查询
            print(query, values)
            cursor.execute(query, values)
            results = cursor.fetchall()
            return results
        except pymysql.MySQLError as e:
            print(f"数据库操作失败：{e}")
            connection.rollback()  # 发生错误时回滚事务
        finally:
            # 关闭连接
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def saveBatchCommonData(self, table, fields, values):
        """
        生成批量插入的 SQL 查询语句。

        参数:
        table (str): 表名
        fields (list): 字段名列表
        values (list of tuples): 要插入的值的列表，每个元素是一个元组，代表一行数据

        返回:
        str: 完整的 SQL 查询语句
        """
        # 用逗号拼接字段名
        fields_string = ", ".join(fields)

        # 根据字段数量生成对应数量的 %s
        placeholders = ", ".join(["%s"] * len(fields))

        try:
            # 创建数据库连接
            connection = pymysql.connect(**self.db_config)
            cursor = connection.cursor()
            # 构造 SQL 语句
            sql = f"INSERT INTO {table} ({fields_string}) VALUES ({placeholders})"

            #print(sql, values)
            # 执行插入操作
            cursor.executemany(sql, values)
            connection.commit()  # 提交事务
            print(f"成功插入 {cursor.rowcount} 行数据到表 {table} 中。")
        except pymysql.MySQLError as e:
            print(f"数据库操作失败：{e}")
            connection.rollback()  # 发生错误时回滚事务
        finally:
            # 关闭连接
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def saveNetData(self, sCode, data):
        str_instance = StringUtil()

        try:
            # 创建数据库连接
            connection = pymysql.connect(**self.db_config)
            cursor = connection.cursor()
            # 插入数据的 SQL 语句
            sql = f"""
            INSERT INTO {DataBase.STOCK_NET_VALUE_TABLE} (code, s_code, name, net_val, acc_val, pre_val, c_date, remark)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            res = str_instance.strToArr(data)
            # 在第一个元素前插入 -1
            res.insert(0, sCode)
            code = sCode.split('_')[1]  # 以下划线分割并取第二部分
            res.insert(0, code)
            print(res)

            # 执行插入操作
            cursor.execute(sql, res)
            connection.commit()  # 提交事务
        except pymysql.MySQLError as e:
            print(f"数据库操作失败：{e}")
            connection.rollback()  # 发生错误时回滚事务
        finally:
            # 关闭连接
            if cursor:
                cursor.close()
            if connection:
                connection.close()

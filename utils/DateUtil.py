import datetime

class DateUtil:
    def safeTimestampToDate(self, timestamp):
        try:
            if timestamp < 0:
                # 处理负数时间戳：可以手动减去对应的时间
                epoch = datetime.datetime(1970, 1, 1)  # Unix 纪元
                return epoch + datetime.timedelta(seconds=timestamp)  # 使用 timedelta 处理负数时间戳
            # 转换正时间戳为 UTC 日期
            return datetime.datetime.utcfromtimestamp(timestamp)
        except OSError as e:
            print(f"Error converting timestamp {timestamp}: {e}")
            return None  # 如果转换失败，返回 None

    def toMysqlDatetime(self, dt):
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%d %H:%M:%S')
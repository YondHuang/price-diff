import re

class StringUtil:

    #字符串转成字符数组
    def strToArr(self, str):
        # 使用正则提取双引号内的内容
        match = re.search(r'="(.*?)"', str)
        if match:
            data = match.group(1)  # 提取双引号内的内容
            split_values = data.split(',')  # 按逗号分割
            print(split_values)
        else:
            print("未找到匹配内容")
        # 将字符串按逗号分割
        split_values = data.strip(',').split(',')

        # 你可以根据需要将这些值转换为适当的类型，比如数字和日期
        converted_values = []
        for value in split_values:
            if value.replace('.', '', 1).isdigit():  # 检查是否是数字
                converted_values.append(float(value) if '.' in value else int(value))
            elif '-' in value and ':' in value:  # 处理日期时间格式
                converted_values.append(value)  # 可以根据需要转换为 datetime 对象
            else:
                converted_values.append(value)

        print(converted_values)
        return converted_values
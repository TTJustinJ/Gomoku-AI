# 定义全局变量
minmax_array = []
randomwalk_array = []

def add_to_minmax_array(data):
    """向全局数组中添加数据"""
    global minmax_array  # 声明使用全局变量
    minmax_array.append(data)

def print_minmax_array():
    """打印全局数组的内容"""
    global minmax_array
    print(minmax_array)

def add_to_randomwalk_array(data):
    """向全局数组中添加数据"""
    global randomwalk_array  # 声明使用全局变量
    randomwalk_array.append(data)

def print_randomwalk_array():
    """打印全局数组的内容"""
    global randomwalk_array
    print(randomwalk_array)

def calculate_minmax_avg():
    global minmax_array
    res = sum(minmax_array) / len(minmax_array) if minmax_array else 0
    return res

def calculate_randomwalk_avg():
    global randomwalk_array
    res = sum(randomwalk_array) / len(randomwalk_array) if randomwalk_array else 0
    return res
# 使用全局数组
# add_to_global_array(10)
# add_to_global_array(20)
# add_to_global_array("Python")
# print_global_array()  # 输出: [10, 20, 'Python']

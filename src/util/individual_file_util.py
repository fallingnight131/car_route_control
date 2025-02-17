import os
import ast

def read_individual(file_path):
    """
    读取个体数据
    :param file_path: 文件路径
    
    :return: 个体数据列表
    """
    individuals = []
    
    # 确保目录存在
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    # 确保文件存在
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass  # 创建空文件
    
    # 读取个体数据
    with open(file_path, "r") as f:
        for line in f:
            individuals.append(ast.literal_eval(line.strip()))
    
    return individuals

def save_individual(file_path, individuals):
    """
    保存个体数据
    :param file_path: 文件路径
    :param individual: 个体数据
    """
    # 确保目录存在
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    # 保存个体数据
    with open(f"file_path", "w") as f:
            for individual in individuals:
                f.write(str(individual) + "\n")

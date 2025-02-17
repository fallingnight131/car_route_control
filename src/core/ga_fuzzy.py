import random
import numpy as np

def random_individual():
    """
    生成一个随机的个体，用于遗传算法的初始化。
    
    返回：
    - List[float] 一个随机的个体
    """
    individual = []
    
    # 定义每个模糊变量的取值范围
    ranges = [(0, 2), (0, 500), (0, 300)]    
    
    # 每个变量有 5 个模糊集，每个模糊集 3 个参数 (左、中、右)
    for low, high in ranges:
        for _ in range(15):
            individual.append(round(random.uniform(low, high), 2))
    
    # 设定固定的索引（转换为 0-based）
    fixed_indices = [0, 1, 13, 14, 15, 16, 28, 29, 30, 31, 43, 44]
    
    # 将固定的索引设置为最大最小值
    for i in range(len(fixed_indices)):
        if i % 4 == 0 or i % 4 == 1:
            individual[fixed_indices[i]] = ranges[i // 4][0]
        if i % 4 == 2 or i % 4 == 3:
            individual[fixed_indices[i]] = ranges[i // 4][1]
        
    return individual

def repair_membership_functions(individual, structure, fixed_indices):
    """
    修复模糊隶属函数参数，确保：
    1. 交界处先交换 (如交换 0.1 和 0.05)。
    2. 整个模糊变量的 15 个参数递增排序。
    3. 交界处再交换回去，确保模糊集完全覆盖。
    4. 指定的索引处参数不会被修改。

    参数：
    - individual: List[float]，个体表示的模糊参数
    - structure: List[int]，每个变量的模糊集数量（如 [5, 5, 5]）
    - fixed_indices: Set[int]，不允许修改的索引集合

    返回：
    - 修复后的 individual（List[float]）
    """
    repaired = individual[:]  # 复制原个体，避免修改原数据
    index = 0  # 当前变量的起始索引

    for num_sets in structure:
        # 获取该变量所有 15 个参数
        params = repaired[index:index + num_sets * 3]

        # 记录交界处的索引
        boundary_indices = [i * 3 - 1 for i in range(1, num_sets)]

        # 交换交界处参数
        for i in boundary_indices:
            if i + 1 < len(params):
                params[i], params[i + 1] = params[i + 1], params[i]

        # 对非固定索引的值进行排序
        sortable_params = [(i, val) for i, val in enumerate(params) if index + i not in fixed_indices]
        sorted_values = sorted(val for _, val in sortable_params)

        for (i, _), val in zip(sortable_params, sorted_values):
            params[i] = val  # 只修改非固定索引的值

        # 交换交界处回来
        for i in boundary_indices:
            if i + 1 < len(params):
                params[i], params[i + 1] = params[i + 1], params[i]

        # **最终检查 a <= b <= c**
        for i in range(num_sets):
            a, b, c = params[i * 3], params[i * 3 + 1], params[i * 3 + 2]
            if not (a <= b <= c):
                params[i * 3:i * 3 + 3] = sorted([a, b, c])  # 强制递增修复

        # 更新 repaired 个体
        repaired[index:index + num_sets * 3] = params
        index += num_sets * 3  # 移动到下一个变量

    return repaired


def generate_offspring(population, n_offspring, structure, bounds, fixed_indices, mutation_rate=0.1, mutation_scale=0.1):
    """
    让多个个体自由繁衍出 n 个子代，并修复每个子代确保覆盖性，并确保参数不超出上下界。

    参数:
    - population: List[List[float]] 现有个体集，每个个体都是一个浮点数列表
    - n_offspring: int 需要生成的子代数量
    - structure: List[int] 每个变量的模糊集数量（如 [5, 5, 5, 5, 5, 5]）
    - bounds: Tuple[List[float], List[float]] 参数的最小值和最大值范围 (lower_bounds, upper_bounds)
    - fixed_indices: Set[int] 不允许修改的索引集合
    - mutation_rate: float 变异率（默认 10%）
    - mutation_scale: float 变异幅度（默认 10%）

    返回:
    - List[List[float]] 生成的 n 个子代
    """
    num_parents = len(population)
    num_genes = len(population[0])
    lower_bounds, upper_bounds = bounds
    offspring = []

    for _ in range(n_offspring):
        # 1. **随机选两个不同的父代**
        parent1, parent2 = random.sample(population, 2)
        
        # 2. **两点交叉**
        point1, point2 = sorted(random.sample(range(num_genes), 2))  # 选两个交叉点
        child = parent1[:point1] + parent2[point1:point2] + parent1[point2:]

        # 3. **变异**
        for i in range(num_genes):
            if i not in fixed_indices and random.random() < mutation_rate:
                mutation = np.random.uniform(-mutation_scale, mutation_scale) * (max(parent1[i], parent2[i]) - min(parent1[i], parent2[i]))
                child[i] = min(max(child[i] + mutation, lower_bounds[i]), upper_bounds[i])  # 确保值在上下界范围内

        # 4. **修复子代**
        repaired_child = repair_membership_functions(child, structure, fixed_indices)
        
        offspring.append(repaired_child)

    return offspring

if __name__ == '__main__':
    # 示例个体（8 个模糊集，每个有 3 个参数）
    individual = [
        0, 0, 0.1, 0.05, 0.3, 0.5, 0.4, 0.6, 0.9, 0.8, 1.2, 1.5, 1.4, 2, 2,  # speed
        0, 0, 3, 2, 8, 12, 10, 50, 90, 80, 120, 250, 200, 350, 500,          # front_dist
        0, 0, 3, 2, 8, 12, 10, 20, 30, 25, 120, 200, 180, 250, 300,          # left_dist
        0, 0, 3, 2, 8, 12, 10, 20, 30, 25, 120, 200, 180, 250, 300,          # right_dist
        -2, -2, -1.5, -1.7, -1, -0.2, -0.4, 0, 0.1, 0.05, 0.1, 0.15, 0.12, 0.2, 0.2,  # acceleration
        -4, -4, -2, -4, -2, 0, -2, 0, 2, 0, 2, 4, 2, 4, 4                     # rotation
    ]

    # 设定模糊系统的结构
    structure = [5, 5, 5, 5, 5, 5]

    # 设定固定的索引（如 1, 15, 16, 30, ...）
    fixed_indices = {1, 15, 16, 30, 45, 60, 75, 90}

    # 设定参数范围（这里假设所有参数的范围为 [0, 10]）
    lower_bounds = [0] * 60 + [-2] * 15 + [-4] * 15
    upper_bounds = [2] * 15 + [500] * 15 + [300] * 30 + [0.2] * 15 + [4] * 15
    bounds = (lower_bounds, upper_bounds)

    # 假设已有父代个体
    population = [[round(random.uniform(0, 10), 2) for _ in range(90)] for _ in range(10)]

    # 生成 5 个子代
    offspring = generate_offspring(population, 5, structure, bounds, fixed_indices)

    # 打印第一个子代
    print(offspring[0])
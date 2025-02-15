import random
import numpy as np

def repair_membership_functions(individual, structure, fixed_indices):
    """
    修复模糊隶属函数参数，确保：
    1. 每个模糊集的3个参数是递增的。
    2. 相邻模糊集的衔接关系满足：后一个的第一个参数 ≥ 前一个的最后一个参数。
    3. 指定的索引处参数不会被修改。

    参数：
    - individual: List[float]，个体表示的模糊参数
    - structure: List[int]，每个变量的模糊集数量（如 [5, 5, 5, 5, 5, 5]）
    - fixed_indices: Set[int]，不允许修改的索引集合

    返回：
    - 修复后的 individual（List[float]）
    """
    repaired = individual[:]
    index = 0

    for num_sets in structure:
        # 取出该变量的所有模糊集参数
        sets = [repaired[index + i * 3: index + (i + 1) * 3] for i in range(num_sets)]

        # 1. **先交换交界处的参数**
        for i in range(1, num_sets):
            sets[i - 1][2], sets[i][0] = sets[i][0], sets[i - 1][2]

        # 2. **确保每个模糊集递增**
        for i in range(num_sets):
            if index + i * 3 not in fixed_indices:
                sets[i] = sorted(sets[i])  # 直接排序保证递增

        # 3. **再交换交界处的参数**
        for i in range(1, num_sets):
            if index + i * 3 not in fixed_indices and index + (i - 1) * 3 + 2 not in fixed_indices:
                sets[i - 1][2], sets[i][0] = max(sets[i - 1][2], sets[i][0]), max(sets[i - 1][2], sets[i][0])

        # 4. **重新拼接**
        repaired[index:index + num_sets * 3] = [val for mf in sets for val in mf]
        index += num_sets * 3

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
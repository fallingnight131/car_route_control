import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl
import random
from deap import base, creator, tools, algorithms

def evaluate(individual):
    """
    适应度评估函数：
    1. 将个体的参数映射到隶属函数
    2. 运行小车仿真
    3. 返回小车通过的检查点数作为适应度
    """
    global speed, front_dist, left_dist, right_dist, acceleration, rotation
    
    # 解码基因
    param_index = 0
    for var in [speed, front_dist, left_dist, right_dist, acceleration, rotation]:
        for label in var.terms:
            var[label] = fuzz.trimf(var.universe, individual[param_index:param_index+3])
            param_index += 3
    
    # 运行仿真，计算小车通过的检查点数量
    checkpoints_passed = simulate_car()
    return (checkpoints_passed,)

def simulate_car():
    """模拟小车运行并返回通过的检查点数量（伪代码）"""
    return random.randint(0, 50)  # 这里可以替换成真实仿真环境

# 定义模糊变量（示例）
speed = ctrl.Antecedent(np.arange(0, 2.1, 0.1), 'speed')
front_dist = ctrl.Antecedent(np.arange(0, 500, 1), 'front_dist')
left_dist = ctrl.Antecedent(np.arange(0, 300, 1), 'left_dist')
right_dist = ctrl.Antecedent(np.arange(0, 300, 1), 'right_dist')
acceleration = ctrl.Consequent(np.arange(-2, 0.2, 0.1), 'acceleration')
rotation = ctrl.Consequent(np.arange(-4, 4.1, 0.1), 'rotation')

# GA 参数
NUM_PARAMS = 3 * 5 * 6  # 每个变量 5 个隶属函数，每个隶属函数 3 个参数，共 6 个变量
POP_SIZE = 20
GENS = 50
CXPB = 0.7
MUTPB = 0.2

# 定义遗传算法
creator.create("FitnessMax", base.Fitness, weights=(1.0,))  # 最大化适应度
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, 0, 500)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=NUM_PARAMS)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=20, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)

# 运行 GA
if __name__ == "__main__":
    pop = toolbox.population(n=POP_SIZE)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("max", np.max)
    
    algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=GENS, stats=stats, halloffame=hof, verbose=True)
    
    print("最优参数：", hof[0])

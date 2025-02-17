import pygame
import time
import os
import sys
from car import Car
# 添加根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.ga_fuzzy import random_individual, repair_membership_functions, generate_offspring
from src.util.individual_file_util import read_individual, save_individual
from src.util.track_file_util import load_track_data

# 初始化 Pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Racing Game - Complex Track")

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# 加载赛道数据
track_outer, track_inner, check_line = load_track_data("src/config/track_info/train.json")
track = [track_outer, track_inner]

font = pygame.font.SysFont(None, 36)  # 默认字体，大小36

# 读取之前的elite    
elite = read_individual("data/ga_train/elite_individual.txt")
             
# 车辆参数
structure = [5, 5, 5]
fixed_indices = [0, 1, 13, 14, 15, 16, 28, 29, 30, 31, 43, 44]
lower_bounds = [0] * 60
upper_bounds = [2] * 15 + [500] * 15 + [300] * 30
bounds = (lower_bounds, upper_bounds)
cars = []
for _ in range(10-len(elite)):
    individual = random_individual()
    # 修复模糊隶属函数参数
    individual = repair_membership_functions(individual, structure, fixed_indices)
    car = Car(individual=individual, pos=[200, 750], angle=0, max_speed=2)
    cars.append(car)

for individual in elite:
    car = Car(individual=individual, pos=[200, 750], angle=0, max_speed=2)
    cars.append(car)
    
# 遗传算法执行多少代
GENERATIONS = 100
running = True
# 遗传算法开始
for generation in range(GENERATIONS):
    if not running:
        break

    start_time = time.time()
    run_time = max((generation + 1) * 60, 240)

    while time.time() - start_time < run_time and running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        car_num = len(cars)
        for car in cars:
            car_points = car.update_info(track, check_line)
            if car_points:
                # 绘制车辆
                pygame.draw.polygon(screen, RED, car_points)
            else:
                car_num -= 1
        
        # 绘制赛道
        pygame.draw.polygon(screen, BLACK, track_outer, 3)
        pygame.draw.polygon(screen, BLACK, track_inner, 3)
        
        # 绘制检查线
        for line in check_line:
            pygame.draw.line(screen, GREEN, line[0], line[1], 2)
            
        # 在右上角打印现在第几代，以及时间还剩多久, 以及剩余几辆车
        text = font.render(f"Generation: {generation + 1}", True, BLACK)
        screen.blit(text, (800, 50))
        text = font.render(f"Time Left: {run_time - int(time.time() - start_time)}s", True, BLACK)
        screen.blit(text, (800, 100))
        text = font.render(f"Cars Left: {car_num}", True, BLACK)
        screen.blit(text, (800, 150))
    
        pygame.display.flip()
        
    if running:
        # 筛选适应度最高的5个存活个体,如果不足5个则全部保留
        elite = []
        cars.sort(key=lambda x: x.fitness, reverse=True)
        for car in cars:
            if len(elite) >= 3:
                break
            else:
                if car.individual not in elite:
                    elite.append(car.individual)
                
        # 保存elite
        save_individual("data/ga_train/elite_individual.txt", elite)
        
        # 生成下一代个体
        cars = []
        next_individuals = generate_offspring(population=elite, n_offspring=8 - len(elite), 
                                            structure=structure, fixed_indices=fixed_indices, 
                                            bounds=bounds)
        next_individuals.extend(elite)
        for individual in next_individuals:
            car = Car(individual=individual, pos=[200, 750], angle=0, max_speed=2)
            cars.append(car)
            
        # 再引入2个随机个体
        for _ in range(2):
            individual = random_individual()
            individual = repair_membership_functions(individual, structure, fixed_indices)
            car = Car(individual=individual, pos=[200, 750], angle=0, max_speed=2)
            cars.append(car)
        
pygame.quit()
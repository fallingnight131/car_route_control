import pygame
import time
import os
import sys
import logging
from car import Car
# 添加根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.ga_fuzzy import random_individual, repair_membership_functions, generate_offspring
from src.util.individual_file_util import read_individual, save_individual
from src.util.track_file_util import load_track_data

# 初始化 Pygame
pygame.init()
running = True

# 设置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

# 读取之前的elite    
elite = read_individual("data/ga_train/elite_individual.txt")
             
# 车辆参数
structure = [5, 5, 5]
fixed_indices = [0, 1, 13, 14, 15, 16, 28, 29, 30, 31, 43, 44]
lower_bounds = [0] * 60
upper_bounds = [2] * 15 + [500] * 15 + [300] * 30
bounds = (lower_bounds, upper_bounds)
car_max_num = 50
cars = []

# 生成车辆
font = pygame.font.Font("src/config/font/msyh.ttc", 36)
for _ in range(car_max_num - len(elite)):
    if not running:
        break
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 显示已经初始化几辆车
    screen.fill(WHITE)
    text = font.render(f"正在生成第1代车辆数据...", True, BLACK)
    screen.blit(text, (300, 300))
    text = font.render(f"请稍等！", True, BLACK)
    screen.blit(text, (300, 350))
    text = font.render(f"已生成：: {len(cars)}/{car_max_num}", True, BLACK)
    screen.blit(text, (300, 400))
    pygame.display.flip()
    pygame.event.pump()

    try:
        individual = random_individual()
        # 修复模糊隶属函数参数
        individual = repair_membership_functions(individual, structure, fixed_indices)
        car = Car(individual=individual, pos=[200, 750], angle=0, max_speed=2)
        cars.append(car)
    except Exception as e:
        logging.info(f"车辆生成失败: {e}")
        continue  # 继续生成下一辆车

    
for individual in elite:
    if not running:
        break
    for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
    # 显示已经初始化几辆车
    screen.fill(WHITE)
    text = font.render(f"正在生成第1代车辆数据...", True, BLACK)
    screen.blit(text, (300, 300))
    text = font.render(f"请稍等！", True, BLACK)
    screen.blit(text, (300, 350))
    text = font.render(f"已生成：: {len(cars)}/{car_max_num}", True, BLACK)
    screen.blit(text, (300, 400))
    pygame.display.flip()
    pygame.event.pump()
    try:
        car = Car(individual=individual, pos=[200, 750], angle=0, max_speed=2)
        cars.append(car)
    except Exception as e:
        logging.info(f"车辆生成失败: {e}")
        continue  # 继续生成下一辆车
    
# 遗传算法执行多少代
GENERATIONS = 100

# 遗传算法开始
for generation in range(GENERATIONS):
    if not running:
        break
    
    font = pygame.font.Font("src/config/font/msyh.ttc", 26)
    start_time = time.time()
    
    while time.time() - start_time < 300 and running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # 按空格键立刻结算这一代
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            break
        
        # 定期处理窗口事件，防止窗口卡死
        pygame.event.pump()
        
        car_num = len(cars)
        max_fitness = 0
        for car in cars:
            car_points = car.update_info_fuzzy(track, check_line)
            max_fitness = max(max_fitness, car.fitness)
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
            
        # 在右上角打印现在第几代，以及时间还剩多久, 剩余几辆车, 最大适应度
        
        text = font.render(f"Generation: {generation + 1}", True, BLACK)
        screen.blit(text, (800, 50))
        text = font.render(f"Time Left: {300 - int(time.time() - start_time)}s", True, BLACK)
        screen.blit(text, (800, 100))
        text = font.render(f"Cars Left: {car_num}", True, BLACK)
        screen.blit(text, (800, 150))
        text = font.render(f"Max Fitness: {max_fitness}", True, BLACK)
        screen.blit(text, (800, 200))
    
        pygame.display.flip()
        pygame.time.delay(5)

    if running:
        # 筛选适应度最高的5个存活个体,如果不足5个则全部保留
        elite = []
        cars.sort(key=lambda x: x.fitness, reverse=True)
        for car in cars:
            if len(elite) >= 10:
                break
            else:
                if car.individual not in elite:
                    elite.append(car.individual)
                
        # 保存elite
        save_individual("data/ga_train/elite_individual.txt", elite)

        # 生成下一代个体
        cars = []
        next_individuals = generate_offspring(population=elite, n_offspring=car_max_num - len(elite), 
                                            structure=structure, fixed_indices=fixed_indices, 
                                            bounds=bounds, crossover_rate=0.8, mutation_rate=0.2, 
                                            mutation_scale=0.1)
        next_individuals.extend(elite)
        
        font = pygame.font.Font("src/config/font/msyh.ttc", 36)
        for individual in next_individuals:
            if not running:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # 显示已经初始化几辆车
            screen.fill(WHITE)
            text = font.render(f"正在生成第{generation + 2}代车辆数据...", True, BLACK)
            screen.blit(text, (300, 300))
            text = font.render(f"请稍等！", True, BLACK)
            screen.blit(text, (300, 350))
            text = font.render(f"已生成：: {len(cars)}/{car_max_num}", True, BLACK)
            screen.blit(text, (300, 400))
            pygame.display.flip()
            pygame.event.pump()
            # 生成车辆
            try:
                car = Car(individual=individual, pos=[200, 750], angle=0, max_speed=2)
                cars.append(car)
            except Exception as e:
                logging.info(f"车辆生成失败: {e}")
                continue  # 继续生成下一辆车
        
pygame.quit()
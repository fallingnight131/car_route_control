import pygame
import time
import concurrent.futures
from ga_fuzzy import random_individual, repair_membership_functions, generate_offspring
from car import Car

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

# **复杂赛道边界**
track_outer = [
    (150, 750), (150, 600), (200, 550), (330, 500), (350, 400),
    (250, 400), (200, 350), (150, 300), (150, 250), (150, 100),
    (300, 50), (500, 100), (650, 200), (750, 350), (850, 400),
    (900, 450), (900, 550), (850, 620), (620, 700), (550, 680),
    (520, 680), (400, 780), (180, 780)
]
track_inner = [
    (200, 700), (250, 600), (300, 550), (380, 530), (400, 500),
    (400, 400), (350, 350), (250, 350), (200, 300), (200, 150),
    (350, 100), (500, 150), (600, 250), (700, 400), (800, 450),
    (850, 500), (850, 550), (800, 600), (650, 650), (530, 630),
    (420, 700), (370, 750), (250, 750)
]
track = [track_outer, track_inner]

# 8个检查线
check_line = [[(350, 750), (350, 780)], [(550, 630), (550, 680)], [(850, 550), (900, 550)],
              [(750, 350), (750, 425)], [(500, 100), (500, 150)], [(150, 150), (200, 150)], 
              [(250, 350), (250, 400)], [(150, 600), (250, 600)]]
font = pygame.font.SysFont(None, 36)  # 默认字体，大小36


# 车辆参数
structure = [5, 5, 5]
fixed_indices = [0, 1, 13, 14, 15, 16, 28, 29, 30, 31, 43, 44]
bounds = [(0, 0, 0), (2, 500, 300)]

# 生成初始 50 辆车
cars = []
for _ in range(50):
    individual = random_individual()
    individual = repair_membership_functions(individual, structure, fixed_indices)
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

    while time.time() - start_time < 180 and running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # **使用并行处理车辆更新**
        car_points_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(lambda car: car.update_info(track, check_line), cars)
            car_points_list = list(results)

        for car_points in car_points_list:
            if car_points:
                pygame.draw.polygon(screen, RED, car_points)

        # 绘制赛道
        pygame.draw.polygon(screen, BLACK, track_outer, 3)
        pygame.draw.polygon(screen, BLACK, track_inner, 3)

        # 绘制检查线
        for line in check_line:
            pygame.draw.line(screen, GREEN, line[0], line[1], 2)
        
        # 在右上角打印现在第几代，以及时间还剩多久
        text = font.render(f"Generation: {generation + 1}", True, BLACK)
        screen.blit(text, (800, 50))
        text = font.render(f"Time Left: {180 - int(time.time() - start_time)}s", True, BLACK)
        screen.blit(text, (800, 100))

        pygame.display.flip()   # 更新屏幕

    # **筛选适应度最高的个体**
    cars.sort(key=lambda x: x.fitness, reverse=True)
    elite = [car.individual for car in cars][:5]

    # **并行生成下一代**
    cars = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        next_individuals = executor.submit(
            generate_offspring, elite, 40 - len(elite), structure, fixed_indices, bounds
        ).result()

    next_individuals.extend(elite)
    for individual in next_individuals:
        cars.append(Car(individual=individual, pos=[200, 750], angle=0, max_speed=2))

    # **再引入 10 个随机个体**
    for _ in range(10):
        individual = random_individual()
        individual = repair_membership_functions(individual, structure, fixed_indices)
        cars.append(Car(individual=individual, pos=[200, 750], angle=0, max_speed=2))

pygame.quit()

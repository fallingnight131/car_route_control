import pygame
import time
import os
import sys
from car import Car
# 添加根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from src.car_route_control.core.ga_fuzzy import random_individual, repair_membership_functions, generate_offspring
from src.car_route_control.util.file_util import read_individual

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
track_outer = [(150, 150), (650, 150), (750, 200), (700, 300), (600, 400), (500, 450), (400, 500), (300, 450), (200, 400), (100, 300), (100, 200)]
track_inner = [(200, 200), (600, 200), (650, 250), (600, 350), (500, 400), (400, 450), (300, 400), (200, 350), (150, 250), (200, 200)]
track = [track_outer, track_inner]

# 8个检查线
check_line = []
font = pygame.font.SysFont(None, 36)  # 默认字体，大小36

# 读取之前的elite    
elite = read_individual("data/elite_individual.txt")
             
# 车辆参数
structure = [5, 5, 5]
fixed_indices = [0, 1, 13, 14, 15, 16, 28, 29, 30, 31, 43, 44]
lower_bounds = [0] * 60
upper_bounds = [2] * 15 + [500] * 15 + [300] * 30
bounds = (lower_bounds, upper_bounds)
if elite:
    car = Car(individual=elite[0], pos=[400, 475], angle=0, max_speed=2)
else:
    individual = random_individual()
    # 修复模糊隶属函数参数
    individual = repair_membership_functions(individual, structure, fixed_indices)
    car = Car(individual=individual, pos=[400, 475], angle=0, max_speed=2)

# 遗传算法执行多少代
GENERATIONS = 100
running = True
# 遗传算法开始
for generation in range(GENERATIONS):
    if not running:
        break

    start_time = time.time()

    while time.time() - start_time < 120 and running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        car_points = car.update_info(track, check_line)
        if car_points:
            # 绘制车辆
            pygame.draw.polygon(screen, RED, car_points)
        else:
            running = False
            print("Car out of track!")
        
        # 绘制赛道
        pygame.draw.polygon(screen, BLACK, track_outer, 3)
        pygame.draw.polygon(screen, BLACK, track_inner, 3)
        
        # 绘制检查线
        for line in check_line:
            pygame.draw.line(screen, GREEN, line[0], line[1], 2)
            
        # 在右上角打印现在小车的速度、前面障碍物的距离、左右障碍物的距离
        speed_text = font.render("Speed: {:.2f}".format(car.speed), True, BLACK)
        screen.blit(speed_text, (800, 50))
        front_text = font.render("Front: {:.2f}".format(car.front_dist), True, BLACK)
        screen.blit(front_text, (800, 100))
        left_text = font.render("Left: {:.2f}".format(car.left_dist), True, BLACK)
        screen.blit(left_text, (800, 150))
        right_text = font.render("Right: {:.2f}".format(car.right_dist), True, BLACK)
        screen.blit(right_text, (800, 200))
    
        pygame.display.flip()
        
pygame.quit()
import pygame
import time
import os
import sys
from car import Car
# 添加根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.ga_fuzzy import random_individual, repair_membership_functions
from src.util.file_util import read_individual

# 添加根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

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
    car = Car(individual=elite[0], pos=[200, 750], angle=0, max_speed=2)
else:
    individual = random_individual()
    # 修复模糊隶属函数参数
    individual = repair_membership_functions(individual, structure, fixed_indices)
    car = Car(individual=individual, pos=[200, 750], angle=0, max_speed=2)

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
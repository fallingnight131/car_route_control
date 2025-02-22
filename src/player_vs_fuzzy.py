import pygame
import os
import sys
# 添加根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.car import Car
from src.util.track_file_util import load_track_data
from src.util.individual_file_util import read_individual
from src.core.ga_fuzzy import random_individual, repair_membership_functions
from src.ui.end_ui import win_ui, lose_ui
from src.ui.init_ui import init_ui_vs
from src.ui.state_ui import state_ui_vs

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
BLUE = (0, 0, 255)

running = True
while running:
    # 加载界面
    init_ui_vs(screen)
    # 玩家操作的车辆参数
    player_car = Car(pos=[180, 750], angle=0, max_speed=2)

    # 读取之前的elite    
    elite = read_individual("data/ga_train/elite_individual.txt")

    # 模糊控制操作的车辆参数
    structure = [5, 5, 5]
    fixed_indices = [0, 1, 13, 14, 15, 16, 28, 29, 30, 31, 43, 44]
    lower_bounds = [0] * 60
    upper_bounds = [2] * 15 + [500] * 15 + [300] * 30
    bounds = (lower_bounds, upper_bounds)
    if elite:
        fuzzy_car = Car(individual=elite[0], pos=[180, 750], angle=0, max_speed=2)
    else:
        individual = random_individual()
        # 修复模糊隶属函数参数
        individual = repair_membership_functions(individual, structure, fixed_indices)
        fuzzy_car = Car(individual=individual, pos=[180, 750], angle=0, max_speed=2)

    # 加载赛道数据
    track_outer, track_inner, check_line = load_track_data("src/config/track_info/vs.json")
    track = [track_outer, track_inner]

    while True:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not running:
            break
        
        # 模糊控制部分
        car_points_fuzzy = fuzzy_car.update_info_fuzzy(track, check_line)
        if car_points_fuzzy:
            # 绘制车辆
            pygame.draw.polygon(screen, RED, car_points_fuzzy)
            
        # 人类部分
        keys = pygame.key.get_pressed()
        car_points_player = player_car.update_info_player(keys, track, check_line)
        if car_points_player:
            # 绘制车辆
            pygame.draw.polygon(screen, BLUE, car_points_player)

        # 绘制赛道和终点
        pygame.draw.polygon(screen, BLACK, track_outer, 3)
        pygame.draw.polygon(screen, BLACK, track_inner, 3)
        
        # 绘制检查线
        for line in check_line:
            pygame.draw.line(screen, GREEN, line[0], line[1], 2)
            
        # 绘制状态信息
        state_ui_vs(screen)
        
        # 检测是否到达终点
        if player_car.fitness >= 1:
            running = win_ui(screen, WIDTH, HEIGHT)
            break
        elif fuzzy_car.fitness >= 1:
            running = lose_ui(screen, WIDTH, HEIGHT)
            break
        
        # 检测是否碰到边界
        if not player_car.alive:
            running = lose_ui(screen, WIDTH, HEIGHT)
            break
        elif not fuzzy_car.alive:
            running = win_ui(screen, WIDTH, HEIGHT)
            break
            
        pygame.display.flip()
        pygame.time.delay(7)
        
pygame.quit()
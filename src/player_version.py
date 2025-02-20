import pygame
import math
import csv
import uuid
import os
import sys
# 添加根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.util.track_file_util import load_track_data
from src.core.car import Car

# 初始化 Pygame
pygame.init()

# 生成唯一 ID
unique_id = uuid.uuid4().hex  
    
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

# 创建车辆
car = Car(pos=[200, 750], angle=0, max_speed=2)

# 加载赛道数据
track_outer, track_inner, check_line = load_track_data("src/config/track_info/player.json")
track = [track_outer, track_inner]

# 创建 data 文件夹
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data/player')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 数据记录
player_data = []

running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    car_points_player = car.update_info_player(keys, track, check_line)
    if car_points_player:
        # 绘制车辆
        pygame.draw.polygon(screen, BLUE, car_points_player)
 
    # 碰撞检测
    if not car.alive:
        print("Game Over: Collision Detected")
        running = False
    
    # 检测是否到达终点
    if car.fitness >= 1:
        print("Success: Reached Goal")
        with open(f"{data_dir}/player_data_{unique_id}.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Speed", "Front Distance", "Left Distance", "Right Distance", "Action", "Acceleration"])
            writer.writerows(player_data)
        running = False
    
    # 记录数据
    action = "left" if keys[pygame.K_LEFT] else "right" if keys[pygame.K_RIGHT] else "straight"
    accel = "accelerate" if keys[pygame.K_SPACE] else "decelerate"
    player_data.append([car.speed, car.front_dist, car.left_dist, car.right_dist, action, accel])
    
    # 绘制赛道和终点
    pygame.draw.polygon(screen, BLACK, track_outer, 3)
    pygame.draw.polygon(screen, BLACK, track_inner, 3)
    pygame.draw.line(screen, GREEN, check_line[0][0], check_line[0][1], 5)
    
    pygame.display.flip()
    pygame.time.delay(10)
    
pygame.quit()
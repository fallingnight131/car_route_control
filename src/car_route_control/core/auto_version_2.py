import pygame
import math
import os
import sys
from fuzzy import FuzzyDriver
# 添加根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# 车辆参数
car_pos = [400, 475]  # 车辆初始位置
car_angle = 0  # 车辆方向（角度）
car_speed = 0  # 车辆速度
ACCELERATION = 0.2  # 加速度
MAX_SPEED = 2  # 最大速度
ROTATION_SPEED = 4  # 旋转速率（度）

# **复杂赛道边界**
track_outer = [(100, 100), (700, 100), (750, 200), (700, 300), (600, 400), (500, 450), (400, 500), (300, 450), (200, 400), (100, 300), (50, 200), (100, 100)]
track_inner = [(200, 200), (600, 200), (650, 250), (600, 350), (500, 400), (400, 450), (300, 400), (200, 350), (150, 250), (200, 200)]


# 数据记录
player_data = []

def distance(point1, point2):
    """计算欧几里得距离"""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def find_nearest_obstacle(car_pos, car_angle, track):
    """计算车辆前方、左侧、右侧最近的赛道边界点"""
    directions = [0, 90, -90]  # 前方、左侧、右侧
    min_distances = [float('inf'), float('inf'), float('inf')]

    for i, direction in enumerate(directions):
        angle = math.radians(car_angle + direction)
        start = car_pos
        end = (car_pos[0] + math.cos(angle) * WIDTH, car_pos[1] - math.sin(angle) * HEIGHT)

        for j in range(len(track)):
            p1, p2 = track[j], track[(j + 1) % len(track)]
            intersect = line_intersection(start, end, p1, p2)
            if intersect:
                min_distances[i] = min(min_distances[i], distance(car_pos, intersect))

    return min_distances

def line_intersection(A, B, C, D):
    """计算两条线段 AB 和 CD 是否相交，返回交点"""
    def ccw(P, Q, R):
        return (R[1] - P[1]) * (Q[0] - P[0]) > (Q[1] - P[1]) * (R[0] - P[0])

    if ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D):
        # 计算交点
        dx1, dy1 = B[0] - A[0], B[1] - A[1]
        dx2, dy2 = D[0] - C[0], D[1] - C[1]
        denom = dx1 * dy2 - dy1 * dx2

        if denom == 0:
            return None

        t = ((A[0] - C[0]) * dy2 - (A[1] - C[1]) * dx2) / denom
        return (A[0] + t * dx1, A[1] + t * dy1)

    return None

individual = [
    0, 0, 0.1, 0.05, 0.3, 0.5, 0.4, 0.6, 0.9, 0.8, 1.2, 1.5, 1.4, 2, 2,  # speed
    0, 0, 3, 2, 8, 12, 10, 50, 90, 80, 120, 250, 200, 350, 500,          # front_dist
    0, 0, 3, 2, 8, 12, 10, 20, 30, 25, 120, 200, 180, 250, 300,          # left_dist
]
    
driver = FuzzyDriver(individual)

# 初始化字体
pygame.font.init()
font = pygame.font.SysFont(None, 36)  # 默认字体，大小36

running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    left = keys[pygame.K_LEFT]
    right = keys[pygame.K_RIGHT]
    accelerate = keys[pygame.K_SPACE]
 
    # 计算前方、左侧、右侧最近的障碍物距离
    outer_distances = find_nearest_obstacle(car_pos, car_angle, track_outer)
    inner_distances = find_nearest_obstacle(car_pos, car_angle, track_inner)

    # 取更小的那一组距离
    front_dist = min(outer_distances[0], inner_distances[0])
    left_dist = min(outer_distances[1], inner_distances[1])
    right_dist = min(outer_distances[2], inner_distances[2])

    # 碰撞检测
    if front_dist < 0 or left_dist < 0 or right_dist < 0:
        print("Game Over: Collision Detected")
        running = False
    
    # 模糊控制
    acceleration, rotation = driver.predict(car_speed, front_dist, left_dist, right_dist)
    
    if acceleration > 0:
        car_speed = min(car_speed + acceleration, MAX_SPEED)
    else:
        car_speed = max(car_speed + acceleration, 0)
        
    car_angle += rotation
        
    rad = math.radians(car_angle)
    car_pos[0] += math.cos(rad) * car_speed
    car_pos[1] -= math.sin(rad) * car_speed
    
    # 绘制赛道
    pygame.draw.polygon(screen, BLACK, track_outer, 3)
    pygame.draw.polygon(screen, BLACK, track_inner, 3)

    # 绘制车辆（三角形箭头） 
    car_points = [
        (car_pos[0] + math.cos(rad) * 10, car_pos[1] - math.sin(rad) * 10),
        (car_pos[0] + math.cos(rad + 2.5) * 10, car_pos[1] - math.sin(rad + 2.5) * 10),
        (car_pos[0] + math.cos(rad - 2.5) * 10, car_pos[1] - math.sin(rad - 2.5) * 10)
    ]
    pygame.draw.polygon(screen, RED, car_points)
    
        # 显示车速和距离信息
    text_surface = font.render(f"Speed: {car_speed:.2f}", True, BLACK)
    screen.blit(text_surface, (WIDTH - 200, 20))

    text_surface = font.render(f"Front Dist: {front_dist:.2f}", True, BLACK)
    screen.blit(text_surface, (WIDTH - 200, 50))

    text_surface = font.render(f"Left Dist: {left_dist:.2f}", True, BLACK)
    screen.blit(text_surface, (WIDTH - 200, 80))

    text_surface = font.render(f"Right Dist: {right_dist:.2f}", True, BLACK)
    screen.blit(text_surface, (WIDTH - 200, 110))
    
    pygame.display.flip()
    # pygame.time.delay(30)
    
pygame.quit()
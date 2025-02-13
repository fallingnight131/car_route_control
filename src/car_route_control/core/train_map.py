import pygame
import math
import csv
import uuid
import os
import sys

# 添加根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# 车辆参数
car_pos = [200, 750]  # 车辆初始位置
last_pos = car_pos.copy()  # 上一帧车辆位置
car_angle = 0  # 车辆方向（角度）
car_speed = 0  # 车辆速度
ACCELERATION = 0.2  # 加速度
MAX_SPEED = 6  # 最大速度
ROTATION_SPEED = 4  # 旋转速率（度）

# **复杂赛道边界**
track_outer = [
    (150, 750), (150, 600), (200, 550), (330, 500), (350, 400),
    (250, 400), (200, 350), (150, 300), (150, 250), (150, 100),
    (300, 50), (500, 100), (650, 200), (750, 350), (850, 400),
    (900, 450), (900, 550), (850, 620), (620, 700), (550, 650),
    (520, 680), (450, 780), (180, 780)
]
track_inner = [
    (200, 700), (250, 600), (300, 550), (380, 530), (400, 500),
    (400, 400), (350, 350), (250, 350), (200, 300), (200, 150),
    (350, 100), (500, 150), (600, 250), (700, 400), (800, 450),
    (850, 500), (850, 550), (800, 600), (650, 650), (550, 600),
    (400, 620), (350, 750), (250, 750)
]

# 8个检查线
check_line = [[(350, 750), (350, 780)], [(550, 600), (550, 650)], [(850, 550), (900, 550)],
              [(750, 350), (750, 425)], [(500, 100), (500, 150)], [(150, 150), (200, 150)], 
              [(250, 350), (250, 400)],[(150, 600), (250, 600)]]


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


def has_crossed_line(A, B, last_pos, car_pos):
    """ 判断小车是否穿过了一条检查线 """
    return line_intersection(last_pos, car_pos, A, B) is not None

def update_fitness(car, last_pos, car_pos):
    """ 更新某辆车的适应度 """
    valid_checkpoints = car["valid_checkpoints"]
    A, B = check_line[valid_checkpoints]
    if has_crossed_line(A, B, last_pos, car_pos):
        car["valid_checkpoints"] = (valid_checkpoints + 1) % len(check_line)
        car["fitness"] += 1
            
cars = [
    {"id": 1, "fitness": 0, "valid_checkpoints": 0}  # 只有第1个检查线最初有效
]
            
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
    if front_dist < 5 or left_dist < 5 or right_dist < 5:
        print("Game Over: Collision Detected")
        running = False
    
    # 检测是否到检查线
    update_fitness(cars[0], last_pos, car_pos)
    
    # 记录上一时刻的位置
    last_pos = car_pos.copy()
    
    # 更新车辆信息
    if left:
       car_angle += ROTATION_SPEED
    if right:
        car_angle -= ROTATION_SPEED
    if accelerate:
        car_speed = min(car_speed + ACCELERATION, MAX_SPEED)
    else:
        car_speed = max(car_speed - ACCELERATION, 0)
        
    rad = math.radians(car_angle)
    car_pos[0] += math.cos(rad) * car_speed
    car_pos[1] -= math.sin(rad) * car_speed
    
    # 绘制赛道
    pygame.draw.polygon(screen, BLACK, track_outer, 3)
    pygame.draw.polygon(screen, BLACK, track_inner, 3)
    
    # 绘制检查线
    for line in check_line:
        pygame.draw.line(screen, GREEN, line[0], line[1], 2)
    
    # 绘制车辆（三角形箭头） 
    car_points = [
        (car_pos[0] + math.cos(rad) * 10, car_pos[1] - math.sin(rad) * 10),
        (car_pos[0] + math.cos(rad + 2.5) * 10, car_pos[1] - math.sin(rad + 2.5) * 10),
        (car_pos[0] + math.cos(rad - 2.5) * 10, car_pos[1] - math.sin(rad - 2.5) * 10)
    ]
    # 在右上角显示小车的适应度。
    text = font.render(f"Fitness: {cars[0]['fitness']}", True, BLACK)
    screen.blit(text, (WIDTH - 200, 20))
    
    pygame.draw.polygon(screen, RED, car_points)
    
    pygame.display.flip()
    pygame.time.delay(30)
    
pygame.quit()
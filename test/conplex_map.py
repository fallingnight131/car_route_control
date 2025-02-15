import pygame
import math
import uuid
import random
import os
import sys
from fuzzy import FuzzyDriver
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
car_angle = 0  # 车辆方向（角度）
car_speed = 0  # 车辆速度
ACCELERATION = 0.2  # 加速度
MAX_SPEED = 2  # 最大速度
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


def repair_membership_functions(individual, structure, fixed_indices):
    """
    修复模糊隶属函数参数，确保：
    1. 交界处先交换 (如交换 0.1 和 0.05)。
    2. 整个模糊变量的 15 个参数递增排序。
    3. 交界处再交换回去，确保模糊集完全覆盖。
    4. 指定的索引处参数不会被修改。

    参数：
    - individual: List[float]，个体表示的模糊参数
    - structure: List[int]，每个变量的模糊集数量（如 [5, 5, 5, 5, 5, 5]）
    - fixed_indices: Set[int]，不允许修改的索引集合

    返回：
    - 修复后的 individual（List[float]）
    """
    repaired = individual[:]  # 复制原个体，避免修改原数据
    index = 0  # 当前变量的起始索引

    for num_sets in structure:
        # 获取该变量所有 15 个参数
        params = repaired[index:index + num_sets * 3]

        # 第一步：先交换交界处
        for i in range(1, num_sets):
            params[i * 3 - 1], params[i * 3] = params[i * 3], params[i * 3 - 1]

        # 第二步：整体递增排序（跳过 fixed_indices）
        sortable_params = [
            (i, val) for i, val in enumerate(params) if index + i not in fixed_indices
        ]
        sorted_values = sorted(val for _, val in sortable_params)
        
        for (i, _), val in zip(sortable_params, sorted_values):
            params[i] = val  # 只修改非固定索引的值

        # 第三步：再交换回交界处
        for i in range(1, num_sets):
            params[i * 3 - 1], params[i * 3] = params[i * 3], params[i * 3 - 1]

        # 更新 repaired 个体
        repaired[index:index + num_sets * 3] = params
        index += num_sets * 3  # 移动到下一个变量

    return repaired



def random_individual():
    individual = []
    
    # 定义每个模糊变量的取值范围
    ranges = [(0, 2), (0, 500), (0, 300)]    
    
    # 每个变量有 5 个模糊集，每个模糊集 3 个参数 (左、中、右)
    for low, high in ranges:
        for _ in range(15):
            individual.append(round(random.uniform(low, high),2))
    
    # 设定固定的索引（转换为 0-based）
    fixed_indices = [0, 1, 13, 14, 15, 16, 28, 29, 30, 31, 43, 44]
    
    # 将固定的索引设置为最大最小值
    for i in range(len(fixed_indices)):
        if i % 4 == 0 or i % 4 == 1:
            individual[fixed_indices[i]] = ranges[i // 4][0]
        if i % 4 == 2 or i % 4 == 3:
            individual[fixed_indices[i]] = ranges[i // 4][1]
        
    return individual

individual = random_individual()
structure = [5, 5, 5]
fixed_indices = [0, 1, 13, 14, 15, 16, 28, 29, 30, 31, 43, 44]
# 修复模糊隶属函数参数
individual = repair_membership_functions(individual, structure, fixed_indices)

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
    if front_dist <= 0.3 or left_dist <= 0.3 or right_dist <= 0.3:
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
    
    # 绘制赛道和终点
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
    pygame.time.delay(30)
    
pygame.quit()
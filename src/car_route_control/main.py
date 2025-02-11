import pygame
import math

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

# 车辆参数
car_pos = [200, 750]  # 车辆初始位置
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
    (900, 450), (900, 550), (850, 620), (700, 670), (600, 720),
    (400, 780), (150, 780)
]
track_inner = [
    (250, 700), (250, 600), (300, 550), (380, 530), (400, 500),
    (400, 400), (350, 350), (250, 350), (200, 300), (200, 150),
    (350, 100), (500, 150), (600, 250), (700, 400), (800, 450),
    (850, 500), (850, 550), (800, 600), (650, 650), (550, 700),
    (350, 750), (250, 700)
]

# 判断点是否在多边形内（射线法）
def is_point_inside_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# 游戏主循环
running = True
while running:
    screen.fill(WHITE)
    
    # 事件监听
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 获取键盘输入
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        car_angle += ROTATION_SPEED
    if keys[pygame.K_RIGHT]:
        car_angle -= ROTATION_SPEED
    if keys[pygame.K_SPACE]:
        car_speed = min(car_speed + ACCELERATION, MAX_SPEED)
    else:
        car_speed = max(car_speed - ACCELERATION, 0)
    
    # 计算新位置
    rad = math.radians(car_angle)
    car_pos[0] += math.cos(rad) * car_speed
    car_pos[1] -= math.sin(rad) * car_speed
    
    # **碰撞检测**
    if not is_point_inside_polygon(car_pos, track_outer) or is_point_inside_polygon(car_pos, track_inner):
        print("Game Over: Collision Detected")
        running = False
              
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
    
    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()

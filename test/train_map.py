import pygame
from ga_fuzzy import random_individual, repair_membership_functions
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

# 车辆参数
structure = [5, 5, 5]
fixed_indices = [0, 1, 13, 14, 15, 16, 28, 29, 30, 31, 43, 44]
cars = []
for _ in range(10):
    individual = random_individual()
    # 修复模糊隶属函数参数
    individual = repair_membership_functions(individual, structure, fixed_indices)
    car = Car(individual=individual, pos=[200, 750], angle=0, max_speed=2)
    cars.append(car)

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
track = [track_outer, track_inner]

# 8个检查线
check_line = [[(350, 750), (350, 780)], [(550, 600), (550, 650)], [(850, 550), (900, 550)],
              [(750, 350), (750, 425)], [(500, 100), (500, 150)], [(150, 150), (200, 150)], 
              [(250, 350), (250, 400)],[(150, 600), (250, 600)]]
 
font = pygame.font.SysFont(None, 36)  # 默认字体，大小36

running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    for car in cars:
        car_points = car.update_info(track, check_line)
        if car_points:
            # 绘制车辆
            pygame.draw.polygon(screen, RED, car_points)
    
    # 绘制赛道
    pygame.draw.polygon(screen, BLACK, track_outer, 3)
    pygame.draw.polygon(screen, BLACK, track_inner, 3)
    
    # 绘制检查线
    for line in check_line:
        pygame.draw.line(screen, GREEN, line[0], line[1], 2)
  
    pygame.display.flip()
    pygame.time.delay(30)
    
pygame.quit()
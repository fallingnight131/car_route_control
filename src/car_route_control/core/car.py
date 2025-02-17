import math
import logging
from fuzzy import FuzzyDriver

# 设置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Car:
    def __init__(self, individual, pos=[0, 0], angle=0, max_speed=2):
        """
        车辆个体，适用于遗传算法优化路径跟踪
        :param individual: List[float] 模糊控制参数（遗传算法中的基因）
        :param pos: List[float] 车的初始位置坐标
        :param angle: float 车的朝向角度（0° 指向右）
        :param max_speed: float 最大速度
        :param speed: float 速度
        :param front_dist: float 前方障碍物距离
        :param left_dist: float 左侧障碍物距离
        :param right_dist: float 右侧障碍物距离
        :param max_speed: float 最大速度
        """
        self.individual = individual  # 模糊控制参数
        self.driver = FuzzyDriver(individual)
        self.fitness = 0  # 适应度，初始为 0
        self.pos = list(pos)  # 位置坐标
        self.last_pos = list(pos)  # 上一时刻位置坐标
        self.angle = angle
        self.max_speed = max_speed  # 最大速度
        self.speed = 0  # 速度
        self.front_dist = 0 # 前方障碍物距离
        self.left_dist = 0  # 左侧障碍物距离
        self.right_dist = 0 # 右侧障碍物距离
        self.max_speed = 2  # 最大速度
        self.alive = True  # 是否存活
        self.valid_checkpoints = 0  # 有效检查点编号

    def update_info(self, track, check_line):
        """
        更新车辆位置
        :param track: List[Tuple[float, float]] 赛道坐标
        :param check_line: List[Tuple[Tuple[float, float], Tuple[float, float]]] 检查线坐标
        """
        if not self.alive:
            return None
        
        track_outer, track_inner = track
        outer_distances = self.find_nearest_obstacle(self.pos, self.angle, track_outer)
        inner_distances = self.find_nearest_obstacle(self.pos, self.angle, track_inner)
        # 取更小的那一组距离
        self.front_dist = min(outer_distances[0], inner_distances[0])
        self.left_dist = min(outer_distances[1], inner_distances[1])
        self.right_dist = min(outer_distances[2], inner_distances[2])
        
        # 出界检测
        if self.has_crossed_polygon(self.last_pos, self.pos, track_outer) or self.has_crossed_polygon(self.last_pos, self.pos, track_inner):
            self.alive = False
            
        # 检测是否到检查线
        self.update_fitness(check_line)
        
        # 记录上一时刻的位置
        self.last_pos = self.pos.copy()
        
        # 模糊控制
        acceleration, rotation = self.driver.predict(self.speed, self.front_dist, self.left_dist, self.right_dist)
        
        # 判断是否搁浅
        if self.speed ==0 and acceleration <= 0 and rotation == 0:
            self.alive = False
        
        if acceleration > 0:
            self.speed = min(self.speed + acceleration, self.max_speed)
        else:
            self.speed = max(self.speed + acceleration, 0)
            
        self.angle += rotation
        rad = math.radians(self.angle)
        
        # 更新位置
        self.pos[0] += math.cos(rad) * self.speed
        self.pos[1] -= math.sin(rad) * self.speed
        
        # 更新车辆的三角形箭头坐标, 用于绘制
        car_points = [
        (self.pos[0] + math.cos(rad) * 10, self.pos[1] - math.sin(rad) * 10),
        (self.pos[0] + math.cos(rad + 2.5) * 10, self.pos[1] - math.sin(rad + 2.5) * 10),
        (self.pos[0] + math.cos(rad - 2.5) * 10, self.pos[1] - math.sin(rad - 2.5) * 10)
        ]
        
        return car_points
        
    def evaluate_fitness(self, checkpoints):
        """
        计算适应度，基于通过的检查点数
        :param checkpoints: List[Tuple[float, float]] 检查点坐标
        """
        passed = 0
        for cx, cy in checkpoints:
            distance = math.hypot(self.x - cx, self.y - cy)
            if distance < 10:  # 假设 10 为通过的距离阈值
                passed += 1

        self.fitness = passed  # 适应度 = 通过的检查点数
        
    def distance(self, point1, point2):
        """计算欧几里得距离"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def find_nearest_obstacle(self, car_pos, car_angle, track):
        """计算车辆前方、左侧、右侧最近的赛道边界点"""
        WIDTH, HEIGHT = 1000, 800
        directions = [0, 90, -90]  # 前方、左侧、右侧
        min_distances = [float('inf'), float('inf'), float('inf')]

        for i, direction in enumerate(directions):
            angle = math.radians(car_angle + direction)
            start = car_pos
            end = (car_pos[0] + math.cos(angle) * WIDTH, car_pos[1] - math.sin(angle) * HEIGHT)

            for j in range(len(track)):
                p1, p2 = track[j], track[(j + 1) % len(track)]
                intersect = self.line_intersection(start, end, p1, p2)
                if intersect:
                    min_distances[i] = min(min_distances[i], self.distance(car_pos, intersect))

        return min_distances

    def line_intersection(self, A, B, C, D):
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


    def has_crossed_line(self, A, B, last_pos, car_pos):
        """ 判断小车是否穿过了一条检查线 """
        return self.line_intersection(last_pos, car_pos, A, B) is not None
    
    def has_crossed_polygon(self, last_pos, car_pos, polygon):
        """
        判断车辆从 last_pos 移动到 car_pos 时是否穿过了多边形边界。
        
        :param last_pos: (x1, y1) 上一时刻的坐标
        :param car_pos: (x2, y2) 现在的坐标
        :param polygon: List[(x, y)] 赛道外边界顶点列表
        :return: bool 是否穿过多边形
        """
        for i in range(len(polygon)):
            A, B = polygon[i], polygon[(i + 1) % len(polygon)]
            if self.has_crossed_line(A, B, last_pos, car_pos):
                return True
        return False


    def update_fitness(self, check_line):
        """ 更新某辆车的适应度 """
        if check_line:
            A, B = check_line[self.valid_checkpoints]
            if self.has_crossed_line(A, B, self.last_pos, self.pos):
                self.valid_checkpoints = (self.valid_checkpoints + 1) % len(check_line)
                self.fitness += 1
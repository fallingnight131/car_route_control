import math
import random

class Car:
    def __init__(self, individual, x=0, y=0, angle=0):
        """
        车辆个体，适用于遗传算法优化路径跟踪
        :param individual: List[float] 模糊控制参数（遗传算法中的基因）
        :param x: float 车的初始 x 坐标
        :param y: float 车的初始 y 坐标
        :param angle: float 车的朝向角度（0° 指向右）
        :param front_dist: float 前方距离
        :param left_dist: float 左侧距离
        :param right_dist: float 右侧距离
        :param speed: float 速度
        :param max_speed: float 最大速度
        """
        self.individual = individual
        self.fitness = 0  # 适应度，初始为 0
        self.x = x
        self.y = y
        self.angle = angle
        front_dist = 0
        left_dist = 0
        right_dist = 0
        self.speed = 0  # 速度
        self.max_speed = 2  # 最大速度

    def update_position(self, acceleration, rotation):
        """
        更新车辆位置
        :param acceleration: float 加速度（正值加速，负值减速）
        :param rotation: float 旋转角度（负值左转，正值右转）
        """
        self.speed = max(0, self.speed + acceleration)  # 确保速度不为负
        self.angle += rotation  # 更新角度
        
        # 计算新位置
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)

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

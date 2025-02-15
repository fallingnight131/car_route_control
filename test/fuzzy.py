import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl

class FuzzyDriver:
    def __init__(self, individual):
        # 定义模糊变量
        self.speed = ctrl.Antecedent(np.arange(0, 2, 0.01), 'speed')
        self.front_dist = ctrl.Antecedent(np.arange(0, 500, 0.1), 'front_dist')
        self.left_dist = ctrl.Antecedent(np.arange(0, 300, 0.1), 'left_dist')
        self.right_dist = ctrl.Antecedent(np.arange(0, 300, 0.1), 'right_dist')
        self.acceleration = ctrl.Consequent(np.array([-2, -1, 0, 0.1, 0.2]), 'acceleration')
        self.rotation = ctrl.Consequent(np.array([-4, -2, 0, 2, 4]), 'rotation')
        
        # 定义模糊隶属函数的标签
        self.speed.automf(names=['NB', 'NS', 'Z', 'PS', 'PB'])
        self.front_dist.automf(names=['NB', 'NS', 'Z', 'PS', 'PB'])
        self.left_dist.automf(names=['NB', 'NS', 'Z', 'PS', 'PB'])
        self.right_dist.automf(names=['NB', 'NS', 'Z', 'PS', 'PB'])
        self.acceleration.automf(names=['DB', 'DS', 'Z', 'AS', 'AB'])
        self.rotation.automf(names=['RB', 'RS', 'Z', 'LS', 'LB'])
        
        # 应用个体参数到模糊变量
        individual = individual +  individual[-15:] + [-2, -2, -1.5, -1.7, -1, -0.2, -0.4, 0, 0.1, 0.05, 0.1, 0.15, 0.12, 0.2, 0.2,  # acceleration
                                    -4, -4, -2, -4, -2, 0, -2, 0, 2, 0, 2, 4, 2, 4, 4  # rotation
                                   ]  # 补充缺失的参数
        
        self.apply_individual_to_fuzzy(individual)
        
        # 创建模糊控制系统
        self.acceleration_ctrl = ctrl.ControlSystem(self.define_acceleration_rules())
        self.rotation_ctrl = ctrl.ControlSystem(self.define_rotation_rules())
        
        self.acceleration_sim = ctrl.ControlSystemSimulation(self.acceleration_ctrl)
        self.rotation_sim = ctrl.ControlSystemSimulation(self.rotation_ctrl)

    def apply_individual_to_fuzzy(self, individual):
        param_index = 0
        for var in [self.speed, self.front_dist, self.left_dist, self.right_dist, self.acceleration, self.rotation]:
            for label in var.terms:
                var[label] = fuzz.trimf(var.universe, individual[param_index:param_index + 3])
                param_index += 3
    
    def define_acceleration_rules(self):
        return [
            ctrl.Rule(self.speed['NB'] & self.front_dist['NB'], self.acceleration['DB']),
            ctrl.Rule(self.speed['NB'] & self.front_dist['NS'], self.acceleration['AS']),
            ctrl.Rule(self.speed['NB'] & self.front_dist['Z'], self.acceleration['AB']),
            ctrl.Rule(self.speed['NB'] & self.front_dist['PS'], self.acceleration['AB']),
            ctrl.Rule(self.speed['NB'] & self.front_dist['PB'], self.acceleration['AB']),
            ctrl.Rule(self.speed['NS'] & self.front_dist['NB'], self.acceleration['DB']),
            ctrl.Rule(self.speed['NS'] & self.front_dist['NS'], self.acceleration['Z']),
            ctrl.Rule(self.speed['NS'] & self.front_dist['Z'], self.acceleration['AS']),
            ctrl.Rule(self.speed['NS'] & self.front_dist['PS'], self.acceleration['AB']),
            ctrl.Rule(self.speed['NS'] & self.front_dist['PB'], self.acceleration['AB']),
            ctrl.Rule(self.speed['Z'] & self.front_dist['NB'], self.acceleration['DB']),
            ctrl.Rule(self.speed['Z'] & self.front_dist['NS'], self.acceleration['Z']),
            ctrl.Rule(self.speed['Z'] & self.front_dist['Z'], self.acceleration['Z']),
            ctrl.Rule(self.speed['Z'] & self.front_dist['PS'], self.acceleration['AS']),
            ctrl.Rule(self.speed['Z'] & self.front_dist['PB'], self.acceleration['AB']),
            ctrl.Rule(self.speed['PS'] & self.front_dist['NB'], self.acceleration['DB']),
            ctrl.Rule(self.speed['PS'] & self.front_dist['NS'], self.acceleration['Z']),
            ctrl.Rule(self.speed['PS'] & self.front_dist['Z'], self.acceleration['Z']),
            ctrl.Rule(self.speed['PS'] & self.front_dist['PS'], self.acceleration['AS']),
            ctrl.Rule(self.speed['PS'] & self.front_dist['PB'], self.acceleration['AB']),
            ctrl.Rule(self.speed['PB'] & self.front_dist['NB'], self.acceleration['DB']),
            ctrl.Rule(self.speed['PB'] & self.front_dist['NS'], self.acceleration['DS']),
            ctrl.Rule(self.speed['PB'] & self.front_dist['Z'], self.acceleration['Z']),
            ctrl.Rule(self.speed['PB'] & self.front_dist['PS'], self.acceleration['Z']),
            ctrl.Rule(self.speed['PB'] & self.front_dist['PB'], self.acceleration['Z'])
        ]
        
    def define_rotation_rules(self):
        return [
            ctrl.Rule(self.left_dist['NB'] & self.right_dist['NB'], self.rotation['Z']),
            ctrl.Rule(self.left_dist['NB'] & self.right_dist['NS'], self.rotation['RS']),
            ctrl.Rule(self.left_dist['NB'] & self.right_dist['Z'], self.rotation['RB']),
            ctrl.Rule(self.left_dist['NB'] & self.right_dist['PS'], self.rotation['RB']),
            ctrl.Rule(self.left_dist['NB'] & self.right_dist['PB'], self.rotation['RB']),
            ctrl.Rule(self.left_dist['NS'] & self.right_dist['NB'], self.rotation['LS']),
            ctrl.Rule(self.left_dist['NS'] & self.right_dist['NS'], self.rotation['Z']),
            ctrl.Rule(self.left_dist['NS'] & self.right_dist['Z'], self.rotation['RS']),
            ctrl.Rule(self.left_dist['NS'] & self.right_dist['PS'], self.rotation['RB']),
            ctrl.Rule(self.left_dist['NS'] & self.right_dist['PB'], self.rotation['RB']),
            ctrl.Rule(self.left_dist['Z'] & self.right_dist['NB'], self.rotation['LB']),
            ctrl.Rule(self.left_dist['Z'] & self.right_dist['NS'], self.rotation['LS']),
            ctrl.Rule(self.left_dist['Z'] & self.right_dist['Z'], self.rotation['Z']),
            ctrl.Rule(self.left_dist['Z'] & self.right_dist['PS'], self.rotation['RS']),
            ctrl.Rule(self.left_dist['Z'] & self.right_dist['PB'], self.rotation['RB']),
            ctrl.Rule(self.left_dist['PS'] & self.right_dist['NB'], self.rotation['LB']),
            ctrl.Rule(self.left_dist['PS'] & self.right_dist['NS'], self.rotation['LB']),
            ctrl.Rule(self.left_dist['PS'] & self.right_dist['Z'], self.rotation['LS']),
            ctrl.Rule(self.left_dist['PS'] & self.right_dist['PS'], self.rotation['Z']),
            ctrl.Rule(self.left_dist['PS'] & self.right_dist['PB'], self.rotation['RS']),
            ctrl.Rule(self.left_dist['PB'] & self.right_dist['NB'], self.rotation['LB']),
            ctrl.Rule(self.left_dist['PB'] & self.right_dist['NS'], self.rotation['LB']),
            ctrl.Rule(self.left_dist['PB'] & self.right_dist['Z'], self.rotation['LB']),
            ctrl.Rule(self.left_dist['PB'] & self.right_dist['PS'], self.rotation['LS']),
            ctrl.Rule(self.left_dist['PB'] & self.right_dist['PB'], self.rotation['Z'])
        ]
    def predict(self, speed, front_dist, left_dist, right_dist):
        self.acceleration_sim.input['speed'] = speed
        self.acceleration_sim.input['front_dist'] = front_dist
        self.acceleration_sim.compute()
        
        fuzzy_accel = [-2,-1,0,0.1,0.2][np.argmin([
            abs(self.acceleration_sim.output['acceleration'] - (-2)),  # 减速
            abs(self.acceleration_sim.output['acceleration'] - (-1)),  # 减速
            abs(self.acceleration_sim.output['acceleration'] - 0),  # 停止
            abs(self.acceleration_sim.output['acceleration'] - 0.1),  # 加速
            abs(self.acceleration_sim.output['acceleration'] - 0.2)  # 加速
        ])]  # 确定加速度值
        
        self.rotation_sim.input['left_dist'] = left_dist
        self.rotation_sim.input['right_dist'] = right_dist
        self.rotation_sim.compute()
        
        fuzzy_rotate = [-2, -1, 0, 1, 2][np.argmin([
                abs(self.rotation_sim.output['rotation'] - (-4)),  # 左转
                abs(self.rotation_sim.output['rotation'] - (-2)),  # 左转
                abs(self.rotation_sim.output['rotation'] - 0),  # 直行
                abs(self.rotation_sim.output['rotation'] - 2),  # 右转
                abs(self.rotation_sim.output['rotation'] - 4)  # 右转
            ])]
        return fuzzy_accel, fuzzy_rotate

# 测试
if __name__ == '__main__':
    individual = [
        0, 0, 0.1, 0.05, 0.3, 0.5, 0.4, 0.6, 0.9, 0.8, 1.2, 1.5, 1.4, 2, 2,  # speed
        0, 0, 3, 2, 8, 12, 10, 50, 90, 80, 120, 250, 200, 350, 500,          # front_dist
        0, 0, 3, 2, 8, 12, 10, 20, 30, 25, 120, 200, 180, 250, 300,          # left_dist
        0, 0, 3, 2, 8, 12, 10, 20, 30, 25, 120, 200, 180, 250, 300,          # right_dist
    ]
    driver = FuzzyDriver(individual)
    acceleration, rotation = driver.predict(1, 205.4, 45, 10.0)
    print(f"Acceleration: {acceleration}, Rotation: {rotation}")

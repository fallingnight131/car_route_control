import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl

class FuzzyDriver:
    def __init__(self, individual, 
                 speed_step=0.2, 
                 front_step=20, 
                 left_step=20, 
                 right_step=20):
        # 原有模糊系统初始化代码
        self.speed = ctrl.Antecedent(np.arange(0, 2, 0.01), 'speed')
        self.front_dist = ctrl.Antecedent(np.arange(0, 500, 0.1), 'front_dist')
        self.left_dist = ctrl.Antecedent(np.arange(0, 300, 0.1), 'left_dist')
        self.right_dist = ctrl.Antecedent(np.arange(0, 300, 0.1), 'right_dist')
        self.acceleration = ctrl.Consequent(np.array([-2, -1, 0, 0.1, 0.2]), 'acceleration')
        self.rotation = ctrl.Consequent(np.array([-4, -2, 0, 2, 4]), 'rotation')

        self.speed.automf(names=['NB', 'NS', 'Z', 'PS', 'PB'])
        self.front_dist.automf(names=['NB', 'NS', 'Z', 'PS', 'PB'])
        self.left_dist.automf(names=['NB', 'NS', 'Z', 'PS', 'PB'])
        self.right_dist.automf(names=['NB', 'NS', 'Z', 'PS', 'PB'])
        self.acceleration.automf(names=['DB', 'DS', 'Z', 'AS', 'AB'])
        self.rotation.automf(names=['RB', 'RS', 'Z', 'LS', 'LB'])

        individual = individual + individual[-15:] + [-2, -2, -1.5, -1.7, -1, -0.2, -0.4, 0, 0.1, 0.05, 
                                                      0.1, 0.15, 0.12, 0.2, 0.2, -4, -4, -2, -4, -2, 
                                                      0, -2, 0, 2, 0, 2, 4, 2, 4, 4]
        self.apply_individual_to_fuzzy(individual)

        self.acceleration_ctrl = ctrl.ControlSystem(self.define_acceleration_rules())
        self.rotation_ctrl = ctrl.ControlSystem(self.define_rotation_rules())
        
        # 创建仿真器但不存储在self中
        self._accel_sim = ctrl.ControlSystemSimulation(self.acceleration_ctrl)
        self._rotate_sim = ctrl.ControlSystemSimulation(self.rotation_ctrl)

        # 查表参数
        self.speed_step = speed_step
        self.front_step = front_step
        self.left_step = left_step
        self.right_step = right_step

        # 预生成查找表
        self.accel_table, self.speed_points, self.front_points = self._build_accel_table()
        self.rotation_table, self.left_points, self.right_points = self._build_rotation_table()

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
        
    def _build_accel_table(self):
        """生成加速度查找表"""
        speed_points = np.arange(0, 2 + 1e-9, self.speed_step)
        front_points = np.arange(0, 500 + 1e-9, self.front_step)
        table = np.zeros((len(speed_points), len(front_points)))

        for i, s in enumerate(speed_points):
            for j, f in enumerate(front_points):
                self._accel_sim.input['speed'] = s
                self._accel_sim.input['front_dist'] = f
                self._accel_sim.compute()
                output = self._accel_sim.output['acceleration']
                table[i, j] = self._discretize_accel(output)
        return table, speed_points, front_points

    def _build_rotation_table(self):
        """生成转向查找表"""
        left_points = np.arange(0, 300 + 1e-9, self.left_step)
        right_points = np.arange(0, 300 + 1e-9, self.right_step)
        table = np.zeros((len(left_points), len(right_points)))

        for i, l in enumerate(left_points):
            for j, r in enumerate(right_points):
                self._rotate_sim.input['left_dist'] = l
                self._rotate_sim.input['right_dist'] = r
                self._rotate_sim.compute()
                output = self._rotate_sim.output['rotation']
                table[i, j] = self._discretize_rotate(output)
        return table, left_points, right_points

    def _discretize_accel(self, value):
        """将连续加速度值离散化"""
        options = np.array([-2, -1, 0, 0.1, 0.2])
        return options[np.argmin(np.abs(value - options))]

    def _discretize_rotate(self, value):
        """将连续转向值离散化"""
        options = np.array([-4, -2, 0, 2, 4])
        return options[np.argmin(np.abs(value - options))]

    def predict(self, speed, front_dist, left_dist, right_dist):
        """使用查找表快速预测"""
        # 计算加速度索引
        speed_idx = self._find_nearest_index(speed, self.speed_points)
        front_idx = self._find_nearest_index(front_dist, self.front_points)
        
        # 计算转向索引
        left_idx = self._find_nearest_index(left_dist, self.left_points)
        right_idx = self._find_nearest_index(right_dist, self.right_points)
        
        return (
            self.accel_table[speed_idx, front_idx],
            self.rotation_table[left_idx, right_idx]
        )

    def _find_nearest_index(self, value, points):
        """找到最近点的索引"""
        return np.clip(int(np.round(value / (points[1]-points[0]))), 0, len(points)-1)

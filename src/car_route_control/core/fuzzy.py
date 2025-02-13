import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl

# 1. 定义模糊变量
# 输入变量
speed = ctrl.Antecedent(np.arange(0, 2, 0.01), 'speed')  # 速度范围：0 到 2
front_dist = ctrl.Antecedent(np.arange(0, 500, 0.1), 'front_dist')  # 前方距离范围：0 到 300
left_dist = ctrl.Antecedent(np.arange(0, 300, 0.1), 'left_dist')  # 左侧距离范围：0 到 50
right_dist = ctrl.Antecedent(np.arange(0, 300, 0.1), 'right_dist')  # 右侧距离范围：0 到 50

# 输出变量
acceleration = ctrl.Consequent(np.array([-2, -1, 0, 0.1, 0.2]), 'acceleration')  # 加速度：-0.2（减速）或 0.2（加速）
rotation = ctrl.Consequent(np.array([-4, -2, 0, 2, 4]), 'rotation')  # 旋转方向：-4°（左转）、0°（直行）、4°（右转）

# 2、手动定义输入变量的模糊隶属函数
speed['NB'] = fuzz.trimf(speed.universe, [0, 0, 0.1])
speed['NS'] = fuzz.trimf(speed.universe, [0.05, 0.3, 0.5])
speed['Z'] = fuzz.trimf(speed.universe, [0.4, 0.6, 0.9])
speed['PS'] = fuzz.trimf(speed.universe, [0.8, 1.2, 1.5])
speed['PB'] = fuzz.trimf(speed.universe, [1.4, 2, 2])

front_dist['NB'] = fuzz.trimf(front_dist.universe, [0, 0, 3])
front_dist['NS'] = fuzz.trimf(front_dist.universe, [2, 8, 12])
front_dist['Z'] = fuzz.trimf(front_dist.universe, [10, 50, 90])
front_dist['PS'] = fuzz.trimf(front_dist.universe, [80, 120, 250])
front_dist['PB'] = fuzz.trimf(front_dist.universe, [200, 350, 500])

left_dist['NB'] = fuzz.trimf(left_dist.universe, [0, 0, 3])
left_dist['NS'] = fuzz.trimf(left_dist.universe, [2, 8, 12])
left_dist['Z'] = fuzz.trimf(left_dist.universe, [10, 20, 30])
left_dist['PS'] = fuzz.trimf(left_dist.universe, [25, 120, 200])
left_dist['PB'] = fuzz.trimf(left_dist.universe, [180, 250, 300])

right_dist['NB'] = fuzz.trimf(right_dist.universe, [0, 0, 3])
right_dist['NS'] = fuzz.trimf(right_dist.universe, [2, 8, 12])
right_dist['Z'] = fuzz.trimf(right_dist.universe, [10, 20, 30])
right_dist['PS'] = fuzz.trimf(right_dist.universe, [25, 120, 200])
right_dist['PB'] = fuzz.trimf(right_dist.universe, [180, 250, 300])

# 手动定义输出变量的模糊隶属函数
acceleration['DB'] = fuzz.trimf(acceleration.universe, [-2, -2, -1.5])
acceleration['DS'] = fuzz.trimf(acceleration.universe, [-1.7, -1, -0.2])
acceleration['Z'] = fuzz.trimf(acceleration.universe, [-0.4, 0, 0.1])
acceleration['AS'] = fuzz.trimf(acceleration.universe, [0.05, 0.1, 0.15])
acceleration['AB'] = fuzz.trimf(acceleration.universe, [0.12, 0.2, 0.2])

rotation['RB'] = fuzz.trimf(rotation.universe, [-4, -4, -2])
rotation['RS'] = fuzz.trimf(rotation.universe, [-4, -2, 0])
rotation['Z'] = fuzz.trimf(rotation.universe, [-2, 0, 2])
rotation['LS'] = fuzz.trimf(rotation.universe, [0, 2, 4])
rotation['LB'] = fuzz.trimf(rotation.universe, [2, 4, 4])

# 3. 定义模糊规则
# 加速度规则
rule001 = ctrl.Rule(speed['NB'] & front_dist['NB'], acceleration['DB'])  # 速度慢、前方距离近 -> 减速
rule002 = ctrl.Rule(speed['NB'] & front_dist['NS'], acceleration['AS'])  # 速度慢、前方距离近 -> 减速
rule003 = ctrl.Rule(speed['NB'] & front_dist['Z'], acceleration['AB'])  # 速度慢、前方距离近 -> 减速
rule004 = ctrl.Rule(speed['NB'] & front_dist['PS'], acceleration['AB'])  # 速度慢、前方距离近 -> 减速
rule005 = ctrl.Rule(speed['NB'] & front_dist['PB'], acceleration['AB'])  # 速度慢、前方距离近 -> 减速
rule006 = ctrl.Rule(speed['NS'] & front_dist['NB'], acceleration['DB'])  # 速度慢、前方距离近 -> 减速
rule007 = ctrl.Rule(speed['NS'] & front_dist['NS'], acceleration['Z'])  # 速度慢、前方距离近 -> 减速
rule008 = ctrl.Rule(speed['NS'] & front_dist['Z'], acceleration['AS'])  # 速度慢、前方距离近 -> 减速
rule009 = ctrl.Rule(speed['NS'] & front_dist['PS'], acceleration['AB'])  # 速度慢、前方距离近 -> 减速
rule010 = ctrl.Rule(speed['NS'] & front_dist['PB'], acceleration['AB'])  # 速度慢、前方距离近 -> 减速
rule011 = ctrl.Rule(speed['Z'] & front_dist['NB'], acceleration['DB'])  # 速度慢、前方距离近 -> 减速
rule012 = ctrl.Rule(speed['Z'] & front_dist['NS'], acceleration['Z'])  # 速度慢、前方距离近 -> 减速
rule013 = ctrl.Rule(speed['Z'] & front_dist['Z'], acceleration['Z'])  # 速度慢、前方距离近 -> 减速
rule014 = ctrl.Rule(speed['Z'] & front_dist['PS'], acceleration['AS'])  # 速度慢、前方距离近 -> 减速
rule015 = ctrl.Rule(speed['Z'] & front_dist['PB'], acceleration['AB'])  # 速度慢、前方距离近 -> 减速
rule016 = ctrl.Rule(speed['PS'] & front_dist['NB'], acceleration['DB'])  # 速度慢、前方距离近 -> 减速
rule017 = ctrl.Rule(speed['PS'] & front_dist['NS'], acceleration['Z'])  # 速度慢、前方距离近 -> 减速
rule018 = ctrl.Rule(speed['PS'] & front_dist['Z'], acceleration['Z'])  # 速度慢、前方距离近 -> 减速
rule019 = ctrl.Rule(speed['PS'] & front_dist['PS'], acceleration['AS'])  # 速度慢、前方距离近 -> 减速
rule020 = ctrl.Rule(speed['PS'] & front_dist['PB'], acceleration['AB'])  # 速度慢、前方距离近 -> 减速
rule021 = ctrl.Rule(speed['PB'] & front_dist['NB'], acceleration['DB'])  # 速度慢、前方距离近 -> 减速
rule022 = ctrl.Rule(speed['PB'] & front_dist['NS'], acceleration['DS'])  # 速度慢、前方距离近 -> 减速
rule023 = ctrl.Rule(speed['PB'] & front_dist['Z'], acceleration['Z'])  # 速度慢、前方距离近 -> 减速
rule024 = ctrl.Rule(speed['PB'] & front_dist['PS'], acceleration['Z'])  # 速度慢、前方距离近 -> 减速
rule025 = ctrl.Rule(speed['PB'] & front_dist['PB'], acceleration['Z'])  # 速度慢、前方距离近 -> 减速

# 旋转方向规则
rule101 = ctrl.Rule(left_dist['NB'] & right_dist['NB'], rotation['Z'])  # 右侧空闲 -> 右转
rule102 = ctrl.Rule(left_dist['NB'] & right_dist['NS'], rotation['RS'])  # 右侧空闲 -> 右转
rule103 = ctrl.Rule(left_dist['NB'] & right_dist['Z'], rotation['RB'])  # 右侧空闲 -> 右转
rule104 = ctrl.Rule(left_dist['NB'] & right_dist['PS'], rotation['RB'])  # 右侧空闲 -> 右转
rule105 = ctrl.Rule(left_dist['NB'] & right_dist['PB'], rotation['RB'])  # 右侧空闲 -> 右转
rule106 = ctrl.Rule(left_dist['NS'] & right_dist['NB'], rotation['LS'])  # 右侧空闲 -> 右转
rule107 = ctrl.Rule(left_dist['NS'] & right_dist['NS'], rotation['Z'])  # 右侧空闲 -> 右转
rule108 = ctrl.Rule(left_dist['NS'] & right_dist['Z'], rotation['RS'])  # 右侧空闲 -> 右转
rule109 = ctrl.Rule(left_dist['NS'] & right_dist['PS'], rotation['RB'])  # 右侧空闲 -> 右转
rule110 = ctrl.Rule(left_dist['NS'] & right_dist['PB'], rotation['RB'])  # 右侧空闲 -> 右转
rule111 = ctrl.Rule(left_dist['Z'] & right_dist['NB'], rotation['LB'])  # 右侧空闲 -> 右转
rule112 = ctrl.Rule(left_dist['Z'] & right_dist['NS'], rotation['LS'])  # 右侧空闲 -> 右转
rule113 = ctrl.Rule(left_dist['Z'] & right_dist['Z'], rotation['Z'])  # 右侧空闲 -> 右转
rule114 = ctrl.Rule(left_dist['Z'] & right_dist['PS'], rotation['RS'])  # 右侧空闲 -> 右转
rule115 = ctrl.Rule(left_dist['Z'] & right_dist['PB'], rotation['RB'])  # 右侧空闲 -> 右转
rule116 = ctrl.Rule(left_dist['PS'] & right_dist['NB'], rotation['LB'])  # 右侧空闲 -> 右转
rule117 = ctrl.Rule(left_dist['PS'] & right_dist['NS'], rotation['LB'])  # 右侧空闲 -> 右转
rule118 = ctrl.Rule(left_dist['PS'] & right_dist['Z'], rotation['LS'])  # 右侧空闲 -> 右转
rule119 = ctrl.Rule(left_dist['PS'] & right_dist['PS'], rotation['Z'])  # 右侧空闲 -> 右转
rule120 = ctrl.Rule(left_dist['PS'] & right_dist['PB'], rotation['RS'])  # 右侧空闲 -> 右转
rule121 = ctrl.Rule(left_dist['PB'] & right_dist['NB'], rotation['LB'])  # 右侧空闲 -> 右转
rule122 = ctrl.Rule(left_dist['PB'] & right_dist['NS'], rotation['LB'])  # 右侧空闲 -> 右转
rule123 = ctrl.Rule(left_dist['PB'] & right_dist['Z'], rotation['LB'])  # 右侧空闲 -> 右转
rule124 = ctrl.Rule(left_dist['PB'] & right_dist['PS'], rotation['LS'])  # 右侧空闲 -> 右转
rule125 = ctrl.Rule(left_dist['PB'] & right_dist['PB'], rotation['Z'])  # 右侧空闲 -> 右转

# 4. 创建模糊控制系统
acceleration_ctrl = ctrl.ControlSystem([rule001, rule002, rule003, rule004, rule005, rule006, rule007, rule008, rule009, rule010, rule011, rule012, rule013, rule014, rule015, rule016, rule017, rule018, rule019, rule020, rule021, rule022, rule023, rule024, rule025])  # 加速度控制系统
rotation_ctrl = ctrl.ControlSystem([rule101, rule102, rule103, rule104, rule105, rule106, rule107, rule108, rule109, rule110, rule111, rule112, rule113, rule114, rule115, rule116, rule117, rule118, rule119, rule120, rule121, rule122, rule123, rule124, rule125])  # 旋转控制系统

acceleration_sim = ctrl.ControlSystemSimulation(acceleration_ctrl)
rotation_sim = ctrl.ControlSystemSimulation(rotation_ctrl)

# 5. 定义 FuzzyDriver 类
class FuzzyDriver:
    def __init__(self):
        self.acceleration_sim = acceleration_sim
        self.rotation_sim = rotation_sim

    def predict(self, speed, front_dist, left_dist, right_dist):
        # 加速决策
        self.acceleration_sim.input['speed'] = speed  # 设置速度输入
        self.acceleration_sim.input['front_dist'] = front_dist  # 设置前方距离输入
        self.acceleration_sim.compute()  # 计算加速度
        fuzzy_accel = [-2,-1,0,0.1,0.2][np.argmin([
            abs(self.acceleration_sim.output['acceleration'] - (-2)),  # 减速
            abs(self.acceleration_sim.output['acceleration'] - (-1)),  # 减速
            abs(self.acceleration_sim.output['acceleration'] - 0),  # 停止
            abs(self.acceleration_sim.output['acceleration'] - 0.1),  # 加速
            abs(self.acceleration_sim.output['acceleration'] - 0.2)  # 加速
        ])]  # 确定加速度值
        # 旋转决策
        self.rotation_sim.input['left_dist'] = left_dist  # 设置左侧距离输入
        self.rotation_sim.input['right_dist'] = right_dist  # 设置右侧距离输入
        self.rotation_sim.compute()  # 计算旋转方向
        try:
            fuzzy_rotate = [-2, -1, 0, 1, 2][np.argmin([
                abs(self.rotation_sim.output['rotation'] - (-4)),  # 左转
                abs(self.rotation_sim.output['rotation'] - (-2)),  # 左转
                abs(self.rotation_sim.output['rotation'] - 0),  # 直行
                abs(self.rotation_sim.output['rotation'] - 2),  # 右转
                abs(self.rotation_sim.output['rotation'] - 4)  # 右转
            ])]
        except:
            fuzzy_rotate = 0

        return fuzzy_accel, fuzzy_rotate  # 返回加速度和旋转方向

# 6. 测试
if __name__ == '__main__':
    driver = FuzzyDriver()
    speed, front_dist, left_dist, right_dist = 5.4, 205.4, 45, 30.0  # 测试输入
    acceleration, rotation = driver.predict(speed, front_dist, left_dist, right_dist)  # 预测
    print(f"Acceleration: {acceleration}, Rotation: {rotation}")  # 输出结果
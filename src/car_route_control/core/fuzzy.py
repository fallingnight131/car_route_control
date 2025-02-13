import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl

# 1. 定义模糊变量
# 输入变量
speed = ctrl.Antecedent(np.arange(0, 1, 0.1), 'speed')  # 速度范围：0 到 6
front_dist = ctrl.Antecedent(np.arange(0, 500, 0.1), 'front_dist')  # 前方距离范围：0 到 300
left_dist = ctrl.Antecedent(np.arange(0, 300, 0.1), 'left_dist')  # 左侧距离范围：0 到 50
right_dist = ctrl.Antecedent(np.arange(0, 300, 0.1), 'right_dist')  # 右侧距离范围：0 到 50

# 输出变量
acceleration = ctrl.Consequent(np.array([-0.2, 0.2]), 'acceleration')  # 加速度：-0.2（减速）或 0.2（加速）
rotation = ctrl.Consequent(np.array([-4, 0, 4]), 'rotation')  # 旋转方向：-4°（左转）、0°（直行）、4°（右转）

# 2. 定义模糊隶属函数
# 自动生成输入变量的模糊隶属函数（低、中、高）
speed.automf(3)
# front_dist.automf(3)
# left_dist.automf(3)
# right_dist.automf(3)


# 手动定义输入变量的模糊隶属函数
front_dist['poor'] = fuzz.trimf(front_dist.universe, [0, 0, 7])
front_dist['average'] = fuzz.trimf(front_dist.universe, [6, 160, 220])
front_dist['good'] = fuzz.trimf(front_dist.universe, [200, 500, 500])

left_dist['poor'] = fuzz.trimf(left_dist.universe, [0, 0, 25])
left_dist['average'] = fuzz.trimf(left_dist.universe, [20, 25, 40])
left_dist['good'] = fuzz.trimf(left_dist.universe, [35, 300, 300])

right_dist['poor'] = fuzz.trimf(right_dist.universe, [0, 0, 25])
right_dist['average'] = fuzz.trimf(right_dist.universe, [20, 25, 40])
right_dist['good'] = fuzz.trimf(right_dist.universe, [35, 300, 300])

# 手动定义输出变量的模糊隶属函数
acceleration['decelerate'] = fuzz.trimf(acceleration.universe, [-0.2, -0.2, 0.2])
acceleration['accelerate'] = fuzz.trimf(acceleration.universe, [-0.2, 0.2, 0.2])

rotation['right'] = fuzz.trimf(rotation.universe, [-4, -4, 0])
rotation['straight'] = fuzz.trimf(rotation.universe, [-4, 0, 4])
rotation['left'] = fuzz.trimf(rotation.universe, [0, 4, 4])

# 3. 定义模糊规则
# 加速度规则
rule11 = ctrl.Rule(speed['poor'] & front_dist['poor'], acceleration['decelerate'])  # 速度慢、前方距离近 -> 减速
rule12 = ctrl.Rule(speed['good'] & front_dist['good'], acceleration['accelerate'])  # 速度快、前方距离远 -> 加速
rule13 = ctrl.Rule(speed['average'] & front_dist['average'], acceleration['accelerate'])  # 速度适中、前方距离适中 -> 加速
rule14 = ctrl.Rule(speed['good'] & front_dist['poor'], acceleration['decelerate'])  # 速度快、前方距离近 -> 加速
rule15 = ctrl.Rule(speed['poor'] & front_dist['good'], acceleration['accelerate'])  # 速度慢、前方距离远 -> 减速
rule16 = ctrl.Rule(speed['average'] & front_dist['poor'], acceleration['decelerate'])  # 速度适中、前方距离近 -> 减速
rule17 = ctrl.Rule(speed['poor'] & front_dist['average'], acceleration['accelerate'])  # 速度慢、前方距离适中 -> 减速
rule18 = ctrl.Rule(speed['good'] & front_dist['average'], acceleration['accelerate'])  # 速度快、前方距离适中 -> 加速
rule19 = ctrl.Rule(speed['average'] & front_dist['good'], acceleration['accelerate'])  # 速度适中、前方距离远 -> 加速

# 旋转方向规则
rule21 = ctrl.Rule(left_dist['poor'] & right_dist['good'], rotation['right'])  # 右侧空闲 -> 右转
rule22 = ctrl.Rule(left_dist['good'] & right_dist['poor'], rotation['left'])  # 左侧空闲 -> 左转
rule23 = ctrl.Rule(left_dist['average'] & right_dist['average'], rotation['straight'])  # 两侧均衡 -> 直行
rule24 = ctrl.Rule(left_dist['good'] & right_dist['good'], rotation['straight'])  # 两侧均衡 -> 直行
rule25 = ctrl.Rule(left_dist['poor'] & right_dist['average'], rotation['right'])  # 左侧空闲 -> 左转
rule26 = ctrl.Rule(left_dist['average'] & right_dist['poor'], rotation['left'])  # 右侧空闲 -> 右转
rule27 = ctrl.Rule(left_dist['poor'] & right_dist['poor'], rotation['straight'])  # 两侧均衡 -> 直行
rule28 = ctrl.Rule(left_dist['good'] & right_dist['average'], rotation['straight'])  # 两侧均衡 -> 直行
rule29 = ctrl.Rule(left_dist['average'] & right_dist['good'], rotation['straight'])  # 两侧均衡 -> 直行
# rule31 = ctrl.Rule(speed['poor'] & front_dist['poor'], rotation['left'])  # 两侧均衡 -> 直行

# 4. 创建模糊控制系统
acceleration_ctrl = ctrl.ControlSystem([rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19])  # 加速度控制系统
rotation_ctrl = ctrl.ControlSystem([rule21, rule22, rule23, rule24, rule25, rule26, rule27, rule28, rule29])  # 旋转控制系统

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
        fuzzy_accel = 0.1 if self.acceleration_sim.output['acceleration'] > 0 else -2  # 确定加速度值

        # 旋转决策
        self.rotation_sim.input['left_dist'] = left_dist  # 设置左侧距离输入
        self.rotation_sim.input['right_dist'] = right_dist  # 设置右侧距离输入
        self.rotation_sim.compute()  # 计算旋转方向
        try:
            fuzzy_rotate = [-2, 0, 2][np.argmin([
                abs(self.rotation_sim.output['rotation'] - (-4)),  # 左转
                abs(self.rotation_sim.output['rotation'] - 0),     # 直行
                abs(self.rotation_sim.output['rotation'] - 4)      # 右转
            ])]
        except:
            print(f"Inputs: left_dist={left_dist}, right_dist={right_dist}")

        return fuzzy_accel, fuzzy_rotate  # 返回加速度和旋转方向

# 6. 测试
if __name__ == '__main__':
    driver = FuzzyDriver()
    speed, front_dist, left_dist, right_dist = 5.4, 205.4, 45, 30.0  # 测试输入
    acceleration, rotation = driver.predict(speed, front_dist, left_dist, right_dist)  # 预测
    print(f"Acceleration: {acceleration}, Rotation: {rotation}")  # 输出结果
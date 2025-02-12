import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl
from sklearn.neural_network import MLPClassifier
import pandas as pd

# 1. 定义模糊控制系统
speed = ctrl.Antecedent(np.arange(0, 10, 0.1), 'speed')
front_dist = ctrl.Antecedent(np.arange(0, 300, 1), 'front_dist')
left_dist = ctrl.Antecedent(np.arange(0, 100, 1), 'left_dist')
right_dist = ctrl.Antecedent(np.arange(0, 100, 1), 'right_dist')

acceleration = ctrl.Consequent(np.arange(-1, 1.1, 0.1), 'acceleration')
rotation = ctrl.Consequent(np.arange(-1, 1.1, 0.1), 'rotation')

# 定义模糊隶属函数
speed.automf(3)
front_dist.automf(3)
left_dist.automf(3)
right_dist.automf(3)

acceleration['decelerate'] = fuzz.trimf(acceleration.universe, [-1, -0.5, 0])
acceleration['maintain'] = fuzz.trimf(acceleration.universe, [-0.5, 0, 0.5])
acceleration['accelerate'] = fuzz.trimf(acceleration.universe, [0, 0.5, 1])

rotation['left'] = fuzz.trimf(rotation.universe, [-1, -0.5, 0])
rotation['straight'] = fuzz.trimf(rotation.universe, [-0.5, 0, 0.5])
rotation['right'] = fuzz.trimf(rotation.universe, [0, 0.5, 1])

# 定义模糊规则
rule1 = ctrl.Rule(front_dist['poor'], acceleration['decelerate'])
rule2 = ctrl.Rule(front_dist['good'], acceleration['accelerate'])
rule3 = ctrl.Rule(left_dist['poor'] & right_dist['good'], rotation['right'])
rule4 = ctrl.Rule(right_dist['poor'] & left_dist['good'], rotation['left'])
rule5 = ctrl.Rule(left_dist['average'] & right_dist['average'], rotation['straight'])

# 创建模糊控制系统
acceleration_ctrl = ctrl.ControlSystem([rule1, rule2])
rotation_ctrl = ctrl.ControlSystem([rule3, rule4, rule5])

acceleration_sim = ctrl.ControlSystemSimulation(acceleration_ctrl)
rotation_sim = ctrl.ControlSystemSimulation(rotation_ctrl)

# 2. 训练 BP 神经网络
class IntelligentDriver:
    def __init__(self):
        self.model = MLPClassifier(hidden_layer_sizes=(10, 10), max_iter=500)
    
    def train(self, data_file):
        df = pd.read_csv(data_file)
        X = df.iloc[:, :4].values
        y_accel = (df.iloc[:, 4] == 'accelerate').astype(int)  # 1 for accelerate, 0 for decelerate
        y_rotate = df.iloc[:, 5].map({'left': -1, 'straight': 0, 'right': 1}).values
        self.model.fit(X, np.column_stack((y_accel, y_rotate)))
    
    def predict(self, speed, front_dist, left_dist, right_dist):
        acceleration_sim.input['speed'] = speed
        acceleration_sim.input['front_dist'] = front_dist
        acceleration_sim.compute()
        fuzzy_accel = acceleration_sim.output['acceleration']
        
        rotation_sim.input['left_dist'] = left_dist
        rotation_sim.input['right_dist'] = right_dist
        rotation_sim.compute()
        fuzzy_rotate = rotation_sim.output['rotation']
        
        # 使用 BP 神经网络进一步优化
        bp_output = self.model.predict([[speed, front_dist, left_dist, right_dist]])[0]
        final_accel = bp_output[0] if bp_output[0] else fuzzy_accel
        final_rotate = bp_output[1] if bp_output[1] else fuzzy_rotate
        
        return final_accel, final_rotate

# 使用智能驾驶系统
driver = IntelligentDriver()
driver.train('training_data.csv')  # 假设你的数据存储在 training_data.csv

# 示例预测
speed, front_dist, left_dist, right_dist = 0.4, 205.4, 24.7, 30.0
acceleration, rotation = driver.predict(speed, front_dist, left_dist, right_dist)
print(f"Acceleration: {acceleration}, Rotation: {rotation}")

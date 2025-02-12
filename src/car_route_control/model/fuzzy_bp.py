import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

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

# 2. 训练 BP 神经网络（使用 PyTorch）
class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(4, 10)
        self.fc2 = nn.Linear(10, 10)
        self.fc3 = nn.Linear(10, 2)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class IntelligentDriver:
    def __init__(self):
        self.model = NeuralNetwork()
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01)
    
    def train(self, data_file, epochs=500):
        df = pd.read_csv(data_file)
        X = torch.tensor(df.iloc[:, :4].values, dtype=torch.float32)
        y_accel = torch.tensor((df.iloc[:, 4] == 'accelerate').astype(int).values, dtype=torch.float32)
        y_rotate = torch.tensor(df.iloc[:, 5].map({'left': -1, 'straight': 0, 'right': 1}).values, dtype=torch.float32)
        y = torch.column_stack((y_accel, y_rotate))
        
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            output = self.model(X)
            loss = self.criterion(output, y)
            loss.backward()
            self.optimizer.step()
            if epoch % 100 == 0:
                print(f'Epoch {epoch}, Loss: {loss.item()}')
    
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
        input_tensor = torch.tensor([[speed, front_dist, left_dist, right_dist]], dtype=torch.float32)
        bp_output = self.model(input_tensor).detach().numpy()[0]
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

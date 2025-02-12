import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

# 1. 定义模糊控制系统
speed = ctrl.Antecedent(np.arange(0, 6, 0.2), 'speed')
front_dist = ctrl.Antecedent(np.arange(0, 300, 0.1), 'front_dist')
left_dist = ctrl.Antecedent(np.arange(0, 50, 0.1), 'left_dist')
right_dist = ctrl.Antecedent(np.arange(0, 50, 0.1), 'right_dist')

# 只能有两个加速度选项：加速（0.2）或减速（-0.2）
acceleration = ctrl.Consequent(np.array([-0.2, 0.2]), 'acceleration')

# 旋转方向：左转（-4°），直行（0°），右转（4°）
rotation = ctrl.Consequent(np.array([-4, 0, 4]), 'rotation')

# 定义模糊隶属函数
speed.automf(3)
front_dist.automf(3)
left_dist.automf(3)
right_dist.automf(3)

acceleration['decelerate'] = fuzz.trimf(acceleration.universe, [-0.2, -0.2, 0.2])  # 减速
acceleration['accelerate'] = fuzz.trimf(acceleration.universe, [-0.2, 0.2, 0.2])  # 加速

rotation['left'] = fuzz.trimf(rotation.universe, [-4, -4, 0])  # 左转
rotation['straight'] = fuzz.trimf(rotation.universe, [-4, 0, 4])  # 直行
rotation['right'] = fuzz.trimf(rotation.universe, [0, 4, 4])  # 右转

# 定义模糊规则
rule1 = ctrl.Rule(front_dist['poor'], acceleration['decelerate'])  # 距离近 -> 减速
rule2 = ctrl.Rule(front_dist['good'], acceleration['accelerate'])  # 距离远 -> 加速
rule3 = ctrl.Rule(left_dist['poor'] & right_dist['good'], rotation['right'])  # 右侧空闲 -> 右转
rule4 = ctrl.Rule(right_dist['poor'] & left_dist['good'], rotation['left'])  # 左侧空闲 -> 左转
rule5 = ctrl.Rule(left_dist['average'] & right_dist['average'], rotation['straight'])  # 两侧均衡 -> 直行

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
        self.fc3 = nn.Linear(10, 2)  # 输出 2 维: [加速 or 减速, 旋转方向]

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)  # 用于旋转决策

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        accel_output = torch.sigmoid(self.fc3(x)[:, 0])  # 第一列: 加速 or 减速 (0 or 1)
        rotate_output = self.softmax(self.fc3(x)[:, 1:])  # 第二列: 左转/右转/直行
        return accel_output, rotate_output


class IntelligentDriver:
    def __init__(self):
        self.model = NeuralNetwork()
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01)
    
    def train(self, data_file, epochs=500):
        df = pd.read_csv(data_file)
        X = torch.tensor(df.iloc[:, :4].values, dtype=torch.float32)
        y_accel = torch.tensor(df.iloc[:, 4].map({'decelerate': 0, 'accelerate': 1}).values, dtype=torch.float32)  # 0 or 1
        y_rotate = torch.tensor(df.iloc[:, 5].map({'left': 0, 'straight': 1, 'right': 2}).values, dtype=torch.long)  # 0, 1, 2
        y = (y_accel, y_rotate)

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
        fuzzy_accel = 0.2 if acceleration_sim.output['acceleration'] > 0 else -0.2

        rotation_sim.input['left_dist'] = left_dist
        rotation_sim.input['right_dist'] = right_dist
        rotation_sim.compute()
        fuzzy_rotate = np.argmax([
            abs(rotation_sim.output['rotation'] - (-4)),  # 左转
            abs(rotation_sim.output['rotation'] - 0),  # 直行
            abs(rotation_sim.output['rotation'] - 4)  # 右转
        ]) - 1  # [-1, 0, 1] 对应 [-4°, 0°, 4°]

        # BP 神经网络优化
        input_tensor = torch.tensor([[speed, front_dist, left_dist, right_dist]], dtype=torch.float32)
        bp_accel, bp_rotate = self.model(input_tensor)
        
        final_accel = 0.2 if bp_accel.item() > 0.5 else -0.2
        final_rotate = [-4, 0, 4][torch.argmax(bp_rotate).item()]
        
        return final_accel, final_rotate


# 训练和测试
driver = IntelligentDriver()
driver.train('training_data.csv')

speed, front_dist, left_dist, right_dist = 0.4, 205.4, 24.7, 30.0
acceleration, rotation = driver.predict(speed, front_dist, left_dist, right_dist)
print(f"Acceleration: {acceleration}, Rotation: {rotation}")

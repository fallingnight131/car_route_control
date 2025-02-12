import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler

# 1. 定义数据集类
class DrivingDataset(Dataset):
    def __init__(self, folder):
        self.data = []
        self.labels_accel = []
        self.labels_rotate = []

        all_X = []  # 收集所有数据用于统一归一化

        # 遍历文件夹，读取所有 CSV 文件
        for file in os.listdir(folder):
            if file.endswith('.csv'):
                df = pd.read_csv(os.path.join(folder, file))

                # 提取输入数据 X
                X = df.iloc[:, :4].apply(pd.to_numeric, errors='coerce').fillna(0).values
                all_X.append(X)  # 先收集所有数据

        # **统一归一化**
        all_X = np.vstack(all_X)  # 把所有数据合并
        self.scaler = MinMaxScaler()
        self.scaler.fit(all_X)  # 在整个数据集上 fit 归一化器

        for file in os.listdir(folder):
            if file.endswith('.csv'):
                df = pd.read_csv(os.path.join(folder, file))

                # 归一化 X
                X = df.iloc[:, :4].apply(pd.to_numeric, errors='coerce').fillna(0).values
                X = self.scaler.transform(X)  # 使用统一的 scaler
                self.data.extend(X)

                # 处理加速度标签 (decelerate:0, accelerate:1)
                df.iloc[:, 5] = df.iloc[:, 5].str.strip().str.lower()
                y_accel = df.iloc[:, 5].map({'decelerate': 0, 'accelerate': 1}).fillna(1)
                self.labels_accel.extend(y_accel)

                # 处理旋转标签 (left:0, straight:1, right:2)
                df.iloc[:, 4] = df.iloc[:, 4].str.strip().str.lower()
                y_rotate = df.iloc[:, 4].map({'left': 0, 'straight': 1, 'right': 2}).fillna(1)
                self.labels_rotate.extend(y_rotate)

        # 转换为 PyTorch 张量
        self.data = torch.tensor(np.array(self.data), dtype=torch.float32)
        self.labels_accel = torch.tensor(np.array(self.labels_accel), dtype=torch.float32).unsqueeze(1)  # BCE 需要 float
        self.labels_rotate = torch.tensor(np.array(self.labels_rotate), dtype=torch.long)  # CrossEntropy 需要 long

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels_accel[idx], self.labels_rotate[idx]


# 2. 定义神经网络
class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(4, 10)
        self.fc2 = nn.Linear(10, 8)
        self.fc3 = nn.Linear(8, 5)  # 新增的隐藏层
        self.fc4_accel = nn.Linear(5, 1)  # 1 维加速度输出
        self.fc4_rotate = nn.Linear(5, 3)  # 3 维旋转输出

        self.relu = nn.LeakyReLU(0.01)  # 替换 ReLU
        self.dropout = nn.Dropout(p=0.3)  # 防止过拟合

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))  # 新增的隐藏层
        accel_output = torch.sigmoid(self.fc4_accel(x))  # 0~1 概率
        rotate_output = self.fc4_rotate(x)  # **不要 Softmax**，因为 CrossEntropyLoss 内部会处理
        return accel_output, rotate_output

# 3. 训练智能驾驶系统
class IntelligentDriver:
    def __init__(self, lr=0.001):
        self.model = NeuralNetwork()
        self.criterion_accel = nn.BCELoss()  # 改为 BCELoss
        self.criterion_rotate = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=500, gamma=0.5)  # 训练时降低学习率

    def train(self, data_folder, epochs=3000, batch_size=32):
        dataset = DrivingDataset(data_folder)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        for epoch in range(epochs):
            total_loss = 0
            for X_batch, y_accel_batch, y_rotate_batch in dataloader:
                self.optimizer.zero_grad()

                output_accel, output_rotate = self.model(X_batch)

                loss_accel = self.criterion_accel(output_accel, y_accel_batch)  # BCELoss
                loss_rotate = self.criterion_rotate(output_rotate, y_rotate_batch)  # CrossEntropy Loss
                loss = loss_accel + loss_rotate

                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()

            self.scheduler.step()  # 逐步降低学习率

            if epoch % 100 == 0:
                print(f'Epoch {epoch}, Loss: {total_loss / len(dataloader):.4f}')
            
            if total_loss < 0.4:
                break

        torch.save(self.model.state_dict(), 'trained_model.pth')
        print("✅ 训练完成，模型已保存为 trained_model.pth")
        
    def predict(self, speed, front_dist, left_dist, right_dist):
        dataset = DrivingDataset("data")  # 读取数据集
        input_data = np.array([[speed, front_dist, left_dist, right_dist]])
        input_data = dataset.scaler.transform(input_data)  # **归一化输入**
        input_tensor = torch.tensor(input_data, dtype=torch.float32)

        bp_accel, bp_rotate = self.model(input_tensor)

        final_accel = 0.2 if bp_accel.item() > 0.5 else -0.2
        final_rotate = [-4, 0, 4][torch.argmax(bp_rotate).item()]

        return final_accel, final_rotate


# 4. 训练模型
driver = IntelligentDriver()
driver.train('data', epochs=50000, batch_size=1000)

# 5. 进行预测
speed, front_dist, left_dist, right_dist = 5.4, 105.4, 24.7, 30.0
acceleration, rotation = driver.predict(speed, front_dist, left_dist, right_dist)
print(f"Acceleration: {acceleration}, Rotation: {rotation}")
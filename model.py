import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn.functional import relu

class Linear_QNet(nn.Module):
    def __init__(self, inputSize, hiddenSize) -> None:
        super().__init__()
        self.inputLayer = nn.Linear(inputSize, hiddenSize)
        self.hiddenLayer = nn.Linear(hiddenSize, hiddenSize)
        self.outputLayer1 = nn.Linear(hiddenSize, 1)
        self.outputLayer2 = nn.Linear(hiddenSize, 1)

    # Current model: input (24) -> linear -> hidden (hiddenSize) -> relu -> linear -> output (2)
    def forward(self, x):
        x = self.inputLayer(x)
        x = relu(x)
        x = self.hiddenLayer(x)
        x = relu(x)
        x1 = self.outputLayer1(x)
        x2 = self.outputLayer2(x)
        return [x1, x2]
    
    # def save(self, fileName):
    #     if not os.path.exists('./Brains'):
    #         os.makedirs('./Brains')
        
    #     torch.save(self.state_dict, os.path.join('./Brains', fileName))

class QTrainer:
    def __init__(self, model: Linear_QNet, learningRate: float, gamma: float) -> None:
        self.lr = learningRate
        self.gamma = gamma
        self.model = model
        self.optimizier = optim.Adam(model.parameters(), learningRate)
        self.criterion = nn.MSELoss()

    def train(self, states, appliedForces, rewards, nextStates):
        states = torch.tensor(states, dtype=torch.float)
        appliedForces = torch.tensor(appliedForces, dtype=torch.float)
        rewards = torch.tensor(rewards, dtype=torch.float)
        nextStates = torch.tensor(nextStates, dtype=torch.float)

        # Check if a tuple of data is passed or just 1 row and if so put it in double array format
        if len(states.shape) == 1:
            states = torch.unsqueeze(states, 0)
            appliedForces = torch.unsqueeze(appliedForces, 0)
            rewards = torch.unsqueeze(rewards, 0)
            nextStates = torch.unsqueeze(nextStates, 0)

        rewards = torch.special.expit(torch.mul(rewards, 0.2))
        predQX = self.model(states)[0]
        predQY = self.model(states)[1]
        QnewX = predQX.clone()
        QnewY = predQY.clone()

        print(predQX, predQY)

        for i in range(len(rewards)):
            QnewX[i] = QnewX[i] * rewards[i] + (1 - rewards[i]) * self.gamma * self.model(nextStates[i])[0]
            QnewY[i] = QnewY[i] * rewards[i] + (1 - rewards[i]) * self.gamma * self.model(nextStates[i])[1]
        
        print(rewards[0])

        self.optimizier.zero_grad()
        lossX = self.criterion(predQX, QnewX)
        lossY = self.criterion(predQY, QnewY)
        loss = lossX + lossY
        loss.backward()
        self.optimizier.step()

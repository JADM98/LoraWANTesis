import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
import copy
import numpy as np
import random

class QNetwork():
    def __init__(self) -> None:
        self.neuralNetwork = nn.Sequential(
            nn.Linear(2, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 5),
        )
        self.gamma = 0.95
        self.lr = 0.0005
        self.optim = AdamW(self.neuralNetwork.parameters(), lr=self.lr)
        self.targetNN = copy.deepcopy(self.neuralNetwork).eval()
        self.counter = 0
        self.epsilon = 0.0
        self.lossArray: np.array = np.array([])

    def evaluate(self, energy:float, sleepTime:float) -> float:
        if self.counter <= 1000:
            self.epsilon = float(0.65 - ( np.power(0.995404, self.counter) ) * 0.65 )
        elif self.counter <= 1500 and self.counter > 1000:
            self.epsilon = 0.65
        else:
            self.epsilon = 0.9

        if (random.random() < self.epsilon):
            actionTaken:torch.Tensor = self.neuralNetwork(torch.tensor([energy, sleepTime]))
            actionTaken = torch.argmax( actionTaken, keepdim=True )
            action = actionTaken.item()
        else:
            action = random.randint(0, 4)

        self.counter += 1

        return int(action)

    def train(self, sampleBatch:torch.Tensor):
        #Sample batch size is what we had in replayMemoryManager batchSize property.
        stateBatch, actionBatch, rewardBatch, nextStateBatch = sampleBatch

        #Evaluation of neural network. 
        #This is the calculation of the current value for bellman equation
        #We get the current Q values of previous states and gather the one whose action was taken previously.
        qValuesBatch = self.neuralNetwork(stateBatch).gather(1, actionBatch)

        #Evaluation of Target neural network
        #This is an estimate of the optimal future value that we should have taken. We get the max Q value.
        targetQValuesBatch = self.targetNN(stateBatch)
        targetQValuesBatch = torch.max(targetQValuesBatch, dim=-1, keepdim=True)[0]

        #Calculation of target value of the bellman equation
        targetValueBatch = rewardBatch + self.gamma * targetQValuesBatch

        #Calculation of loss value
        loss = F.mse_loss(input=qValuesBatch, target=targetValueBatch)

        #Back propagation
        self.neuralNetwork.zero_grad()      #Zeroing gradients
        loss.backward()     
        self.optim.step()

        #Save loss value
        with torch.no_grad():
            self.lossArray = np.concatenate([self.lossArray, [loss.item()]])

        #Each 10 iterations update target Neural Network parameters (thetas).
        if self.counter % 10 == 0:
            self.targetNN.load_state_dict(self.neuralNetwork.state_dict())

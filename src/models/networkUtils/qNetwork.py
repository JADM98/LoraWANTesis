import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
import copy
import numpy as np
import random
from src.models.file_handlers.basic_file_handler import BasicFileHandler

from src.models.networkUtils.qNetworkConstants import QConstants

class QNetwork():

    @property
    def learningRate(self):
        for paramGroup in self.optim.param_groups:
            return paramGroup["lr"]
    @property
    def epoch(self):
        return self.__counter
    
    @property
    def epsilon(self):
        return self.__epsilon

    def __init__(self, counter: int) -> None:
        self.__fileHandler = BasicFileHandler("loss-data.txt")
        self.neuralNetwork = nn.Sequential(
            nn.Linear(2, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, QConstants.NUMBER_OF_ACTIONS),
        )
        self.gamma = QConstants.GAMMA
        self.lr = QConstants.INITIAL_LEARNING_RATE
        self.__counter = counter - QConstants.BATCH_SIZE * QConstants.MINIMUM_TIMES_BS_TO_TRAIN
        if self.__counter < 0:
            self.__counter = 0
        
        self.targetNN = copy.deepcopy(self.neuralNetwork).eval()
        self.__epsilon = 0.0
        lossReads = self.__fileHandler.read()
        if lossReads is None:
            self.lossArray: np.array = np.array([])
        else:
            # self.lossArray: np.array = np.array()
            lossValues = [float(read["loss"]) for read in lossReads]
            self.lossArray: np.array = np.array(lossValues)

        self.optim = AdamW(self.neuralNetwork.parameters(), lr=self.lr)

        if os.path.isfile("model.pth"):
            self.neuralNetwork.load_state_dict(torch.load("model.pth"))
        
        if os.path.isfile("optimizer.pth"):
            state_optimizer = torch.load("optimizer.pth")
            self.optim.load_state_dict(state_optimizer["state_dict"])
            self.learningRateScheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optim, QConstants.STEPS_TO_DECAY_LEARNING_RATE, QConstants.FINAL_LEARNING_RATE, counter)
        else:
            self.learningRateScheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optim, QConstants.STEPS_TO_DECAY_LEARNING_RATE, QConstants.FINAL_LEARNING_RATE)

        self.epochWithoutTrainig = 0

    def evaluateWithNoStep(self, energy:float, sleepTime:float) -> int:
        with torch.no_grad():
            actionTaken:torch.Tensor = self.neuralNetwork(torch.tensor([energy, sleepTime]))
            actionTaken = torch.argmax(actionTaken, keepdim=True)
            action = actionTaken.item()
        return action

    def evaluate(self, energy:float, sleepTime:float) -> int:
        x = self.__counter
        if x <= 250:
            self.__epsilon = float(np.exp(x/360.6738) - 1) * 0.50
        elif x <= 1000 and x > 250:
            self.__epsilon = 0.50
        elif x < 4000:
            self.__epsilon = 0.75
        else:
            self.__epsilon = 0.90

        if (random.random() < self.__epsilon):
            actionTaken:torch.Tensor = self.neuralNetwork(torch.tensor([energy, sleepTime]))
            actionTaken = torch.argmax( actionTaken, keepdim=True )
            action = actionTaken.item()
        else:
            action = random.randint(0, QConstants.NUMBER_OF_ACTIONS - 1)

        self.__counter += 1

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
        targetQValuesBatch = self.targetNN(nextStateBatch)
        targetQValuesBatch = torch.max(targetQValuesBatch, dim=-1, keepdim=True)[0]

        #Calculation of target value of the bellman equation
        targetValueBatch = rewardBatch + self.gamma * targetQValuesBatch

        #Calculation of loss value
        loss = F.mse_loss(input=qValuesBatch, target=targetValueBatch)

        #Back propagation
        self.neuralNetwork.zero_grad()      #Zeroing gradients
        loss.backward()     
        self.optim.step()
        lossValue = loss.item()
        self.__fileHandler.writeDict({
            "loss":str(lossValue)
        })

        # if self.counter < QConstants.STEPS_TO_DECAY_LEARNING_RATE + self.epochWithoutTrainig - 1:
        if self.__counter < QConstants.STEPS_TO_DECAY_LEARNING_RATE - 1:
            self.learningRateScheduler.step()

        #Save loss value
        with torch.no_grad():
            self.lossArray = np.concatenate([self.lossArray, [lossValue]])

        #Each 10 iterations update target Neural Network parameters (thetas).
        if self.__counter % 10 == 0:
            self.targetNN.load_state_dict(self.neuralNetwork.state_dict())
            torch.save(self.neuralNetwork.state_dict(), "model.pth")
            optimizer_state = {
                'state_dict': self.optim.state_dict(),
                'param_groups': self.optim.param_groups,
                'epoch': self.__counter  # Update with the current epoch 
            }
            torch.save(optimizer_state, 'optimizer.pth')

    def exploringIterations(self, epochWithoutTrainig:float) -> None:
        self.epochWithoutTrainig = epochWithoutTrainig

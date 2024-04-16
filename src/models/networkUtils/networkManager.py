from typing import Dict

from src.models.networkUtils.qNetwork import QNetwork
from src.models.devices.loraDevice import LoraDev
from src.models.networkUtils.replayMemoryManager import ReplayMemoryManager
from src.models.networkUtils.rewardCalculator import RewardCalculator
from src.models.networkUtils.qNetworkConstants import QConstants
from src.models.networkUtils.actionState import ActionState

class NetworkManager():
    @property
    def counter(self):
        return self.replayMemoryManager.counter
    @property
    def loss(self):
        return self.qNetwork.lossArray

    def __init__(self, targetEnergy:float = 85.0, replayMemoryCapacity:int=3000, replayMemoryBatchSize:int=16) -> None:
        self.replayMemoryManager = ReplayMemoryManager(capacity=replayMemoryCapacity, batchSize=replayMemoryBatchSize)
        self.qNetwork = QNetwork(self.replayMemoryManager.counter)
        self.qNetwork.exploringIterations(replayMemoryBatchSize * QConstants.MINIMUM_TIMES_BS_TO_TRAIN)
        self.targetEnergy = targetEnergy
        self.actions:list[float] = QConstants.ACTIONS
        self.minimumTS = QConstants.MINIMUM_TS
        self.maximumTS = QConstants.MAXIMUM_TS
        self.differenceTS = QConstants.MAXIMUM_TS - QConstants.MINIMUM_TS
        self.differenceBat = QConstants.MAXIMUM_BAT - QConstants.MINIMUM_BAT

    def getLastTransition(self) -> Dict:
        return self.replayMemoryManager.getLast()

    def evaluateWithNoTrain(self, battery:int, sleepTime:float) -> float:
        action = self.qNetwork.evaluateWithNoStep(energy=battery, sleepTime=sleepTime)
        return self.actions[action]
    
    def getActionWithNoTrain(self, battery:float, sleepTime:float) -> int:
        return self.qNetwork.evaluateWithNoStep(energy=battery, sleepTime=sleepTime)

    def endDaySession(self, device:LoraDev) -> None:
        energy = (device.battery - QConstants.MINIMUM_BAT) / self.differenceBat
        timeSleep = (device.sleepTime - QConstants.MINIMUM_TS) / self.differenceTS

        self.replayMemoryManager.addEndOfDay(device, energy, timeSleep)

    def getNewSleepTime(self, device:LoraDev) -> ActionState:
        #Normalization of data
        energy = (device.battery - QConstants.MINIMUM_BAT) / self.differenceBat
        timeSleep = (device.sleepTime - QConstants.MINIMUM_TS) / self.differenceTS

        action = self.qNetwork.evaluate(energy=energy, sleepTime=timeSleep)
        newSleepTime = self.actions[action] + device.sleepTime

        if newSleepTime < self.minimumTS:
            newSleepTime = self.minimumTS
        if newSleepTime > self.maximumTS:
            newSleepTime = self.maximumTS

        state = ActionState(newSleepTime, action)
        return state
    
    def getNewSleepTimeFromFailure(self, device:LoraDev) -> ActionState:
        #Since we are now adding a failure, we have to decide what to do from the point at this moment.
        #The device has sent new battery, so based on that we will put the sleepTime as 10 minutes.

        #We have to set a defaultSleepTime
        defaultSleepTime = 10.0

        #Normalization of data
        energy = (device.battery - QConstants.MINIMUM_BAT) / self.differenceBat
        timeSleep = (defaultSleepTime - QConstants.MINIMUM_TS) / self.differenceTS
        # stateSleepTime = (device.sleepTime - QConstants.MINIMUM_TS) / self.differenceTS

        #Then we will ask the model what to do now.
        action = self.qNetwork.evaluate(energy=energy, sleepTime=timeSleep)
        newSleepTime = self.actions[action] + defaultSleepTime
        if newSleepTime < self.minimumTS:
            newSleepTime = self.minimumTS
        if newSleepTime > self.maximumTS:
            newSleepTime = self.maximumTS

        return ActionState(newSleepTime, action)
    
    def processState(self, device:LoraDev, state: ActionState) -> None:
        timeSleep = (device.sleepTime - QConstants.MINIMUM_TS) / self.differenceTS
        energy = (device.battery - QConstants.MINIMUM_BAT) / self.differenceBat

        reward = RewardCalculator.calculate(
            energy=device.battery, targetEnergy=self.targetEnergy, sleepTimeChange=self.actions[state.action], currentSleepTime=device.sleepTime)
        
        self.replayMemoryManager.add(device=device, actionTaken=state.action, reward=reward, energy=energy, sleepTime=timeSleep)

        if self.replayMemoryManager.canSample():
            self.qNetwork.train(self.replayMemoryManager.sample())

    def processFailure(self, device:LoraDev, state:ActionState) -> None:
        defaultSleepTime = 10.0

        #Normalization of data
        energy = (device.battery - QConstants.MINIMUM_BAT) / self.differenceBat
        stateSleepTime = (device.sleepTime - QConstants.MINIMUM_TS) / self.differenceTS
        defaultSleepTimeNormalized = (defaultSleepTime - QConstants.MINIMUM_TS) / self.differenceTS

        reward = RewardCalculator.calculate(
            energy=device.battery, targetEnergy=self.targetEnergy, 
            sleepTimeChange=self.actions[state.action], currentSleepTime=defaultSleepTime)

        self.replayMemoryManager.addFailure(
            device=device, actionTaken=state.action, reward=reward, 
            energy=energy, sleepTime=stateSleepTime, defalutSleepTime=defaultSleepTimeNormalized)

        if self.replayMemoryManager.canSample():
            self.qNetwork.train(self.replayMemoryManager.sample())
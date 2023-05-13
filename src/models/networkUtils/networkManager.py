from src.models.networkUtils.qNetwork import QNetwork
from src.models.devices.loraDevice import LoraDev
from src.models.networkUtils.replayMemoryManager import ReplayMemoryManager
from src.models.networkUtils.rewardCalculator import RewardCalculator
from src.models.networkUtils.qNetworkConstants import QConstants

class NetworkManager():
    @property
    def counter(self):
        return self.qNetwork.counter
    @property
    def loss(self):
        return self.qNetwork.lossArray

    def __init__(self, targetEnergy:float = 85.0, replayMemoryCapacity:int=3000, replayMemoryBatchSize:int=16) -> None:
        self.qNetwork = QNetwork()
        self.qNetwork.exploringIterations(replayMemoryBatchSize * QConstants.MINIMUM_TIMES_BS_TO_TRAIN)
        self.replayMemoryManager = ReplayMemoryManager(capacity=replayMemoryCapacity, batchSize=replayMemoryBatchSize)
        self.targetEnergy = targetEnergy
        self.actions:list[float] = QConstants.ACTIONS
        self.minimumTS = QConstants.MINIMUM_TS
        self.maximumTS = QConstants.MAXIMUM_TS
        self.differenceTS = QConstants.MAXIMUM_TS - QConstants.MINIMUM_TS
        self.differenceBat = QConstants.MAXIMUM_BAT - QConstants.MINIMUM_BAT

    def evaluateWithNoTrain(self, battery:int, sleepTime:float) -> float:
        action = self.qNetwork.evaluateWithNoStep(energy=battery, sleepTime=sleepTime)
        return self.actions[action]
    
    def getActionWithNoTrain(self, battery:float, sleepTime:float) -> int:
        return self.qNetwork.evaluateWithNoStep(energy=battery, sleepTime=sleepTime)

    def processNewSleepTime(self, device:LoraDev) -> float:
        #Normalization of data
        energy = (device.battery - QConstants.MINIMUM_BAT) / self.differenceBat
        timeSleep = (device.sleepTime - QConstants.MINIMUM_TS) / self.differenceTS

        action = self.qNetwork.evaluate(energy=energy, sleepTime=timeSleep)
        newSleepTime = self.actions[action] + device.sleepTime

        if newSleepTime < self.minimumTS:
            newSleepTime = self.minimumTS
        if newSleepTime > self.maximumTS:
            newSleepTime = self.maximumTS

        reward = RewardCalculator.calculate(
            energy=device.battery, targetEnergy=self.targetEnergy, sleepTimeChange=self.actions[action], currentSleepTime=device.sleepTime)

        if device.didRestart:
            self.replayMemoryManager.addFailure(device=device)
        
        self.replayMemoryManager.add(device=device, actionTaken=action, reward=reward, energy=energy, sleepTime=timeSleep)

        if self.replayMemoryManager.canSample():
            self.qNetwork.train(self.replayMemoryManager.sample())

        print("Counter: " + str(self.qNetwork.counter) + " Battery: "+str(device.battery)+" SleepTime: "+str(newSleepTime) +" Reward: "+str(round(reward, 4)) + "Action taken: "+str(self.actions[action]))

        return newSleepTime

    def endDaySession(self, device:LoraDev) -> None:
        energy = (device.battery - QConstants.MINIMUM_BAT) / self.differenceBat
        timeSleep = (device.sleepTime - QConstants.MINIMUM_TS) / self.differenceTS

        self.replayMemoryManager.addEndOfDay(device, energy, timeSleep)
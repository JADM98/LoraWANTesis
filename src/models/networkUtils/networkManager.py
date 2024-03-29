from src.models.networkUtils.qNetwork import QNetwork
from src.models.devices.loraDevice import LoraDev
from src.models.networkUtils.replayMemoryManager import ReplayMemoryManager
from src.models.networkUtils.rewardCalculator import RewardCalculator

class NetworkManager():
    @property
    def counter(self):
        return self.qNetwork.counter

    def __init__(self, targetEnergy:float = 80.0, replayMemoryCapacity:int=3000, replayMemoryBatchSize:int=16) -> None:
        self.qNetwork = QNetwork()
        self.replayMemoryManager = ReplayMemoryManager(capacity=replayMemoryCapacity, batchSize=replayMemoryBatchSize)
        self.targetEnergy = targetEnergy
        self.actions:list[float] = [-10,-1, 0, 1, 10]
        self.minimumTS = 1
        self.maximumTS = 60

    def processNewSleepTime(self, device:LoraDev):

        action = self.qNetwork.evaluate(energy=device.battery, sleepTime=device.sleepTime)
        newSleepTime = self.actions[action] + device.sleepTime

        if newSleepTime < self.minimumTS:
            newSleepTime = self.minimumTS
        if newSleepTime > self.maximumTS:
            newSleepTime = self.maximumTS

        reward = RewardCalculator.calculate(
            energy=device.battery, targetEnergy=self.targetEnergy, newSleepTime=self.actions[action], oldSleepTime=device.sleepTime)

        if device.didRestart:
            self.replayMemoryManager.addFailure(device=device)
        
        self.replayMemoryManager.add(device=device, actionTaken=action, reward=reward)

        if self.replayMemoryManager.canSample():
            self.qNetwork.train(self.replayMemoryManager.sample())

        print("Battery: "+str(device.battery)+"SleepTime: "+str(newSleepTime) +" Reward: "+str(reward) + "Action taken: "+str(self.actions[action]))

        return int(newSleepTime)

    
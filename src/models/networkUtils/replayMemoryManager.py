from models.networkUtils.replayMemory import ReplayMemory
from models.networkUtils.transition import Transition
from models.devices.loraDevice import LoraDev
from torch import Tensor

class ReplayMemoryManager():



    def __init__(self, capacity = 3000, batchSize=16) -> None:
        self.replayMemory = ReplayMemory(capacity=capacity, batchSize=batchSize)
        self.currentTrainsitionList:list[Transition] = []

    def add(self, device:LoraDev, actionTaken:int, reward:float) -> None:
        existingTransition = next((tran for tran in self.currentTrainsitionList if tran.id == device.deviceEUI), None)

        transition = Transition(device.deviceEUI, [device.battery, device.sleepTime], actionTaken, reward)
        self.currentTrainsitionList.append(transition)

        if existingTransition is not None:
            self.currentTrainsitionList.remove(existingTransition)
            existingTransition.addNextState([device.battery, device.sleepTime])
            self.replayMemory.insert(existingTransition)

    def addFailure(self, device:LoraDev) -> None:
        existingTransition = next((tran for tran in self.currentTrainsitionList if tran.id == device.deviceEUI), None)

        if existingTransition is not None:
            self.currentTrainsitionList.remove(existingTransition)
            existingTransition.addNextState([float(0), device.oldSleepTime])
            self.replayMemory.insert(existingTransition)
        
    def sample(self) -> list[Tensor]:
        if self.replayMemory.can_sample():
            return self.replayMemory.sampleTensor()
        return None
    
    def sampleList(self) -> list[list[list]]:
        if self.replayMemory.can_sample():
            return self.replayMemory.sampleList()
        return None

    def getMemory(self) -> list[list[list]]:
        return self.replayMemory.getMemoryList()

    def canSample(self) -> bool:
        return self.replayMemory.can_sample()
            
        # [tran for tran in self.currentTrainsitionList if tr]
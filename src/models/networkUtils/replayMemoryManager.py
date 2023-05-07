from src.models.networkUtils.replayMemory import ReplayMemory
from src.models.networkUtils.qNetworkConstants import QConstants
from src.models.networkUtils.transition import Transition
from src.models.devices.loraDevice import LoraDev
from torch import Tensor

class ReplayMemoryManager():



    def __init__(self, capacity = 3000, batchSize=16) -> None:
        self.replayMemory = ReplayMemory(capacity=capacity, batchSize=batchSize)
        self.currentTrainsitionList:list[Transition] = []

    def add(self, device:LoraDev, actionTaken:int, reward:float, energy:float, sleepTime:float) -> None:
        existingTransition = next((tran for tran in self.currentTrainsitionList if tran.id == device.deviceEUI), None)

        transition = Transition(device.deviceEUI, [energy, sleepTime], actionTaken, reward)
        self.currentTrainsitionList.append(transition)

        if existingTransition is not None:
            self.currentTrainsitionList.remove(existingTransition)
            existingTransition.addNextState([energy, sleepTime])
            self.replayMemory.insert(existingTransition)

    def addEndOfDay(self, device:LoraDev, energy:float, sleepTime:float) -> None:
        existingTransition = next((tran for tran in self.currentTrainsitionList if tran.id == device.deviceEUI), None)

        if existingTransition is not None:
            self.currentTrainsitionList.remove(existingTransition)
            existingTransition.addNextState([energy, sleepTime])
            self.replayMemory.insert(existingTransition)

    def addFailure(self, device:LoraDev) -> None:
        existingTransition = next((tran for tran in self.currentTrainsitionList if tran.id == device.deviceEUI), None)

        sleepTime = (device.oldSleepTime - QConstants.MAXIMUM_TS) - (QConstants.MAXIMUM_TS - QConstants.MINIMUM_TS)

        if existingTransition is not None:
            self.currentTrainsitionList.remove(existingTransition)
            existingTransition.addNextState([float(0), sleepTime])
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
from src.models.networkUtils.replayMemory import ReplayMemory
from src.models.networkUtils.qNetworkConstants import QConstants
from src.models.networkUtils.transition import Transition
from src.models.devices.loraDevice import LoraDev
from src.models.file_handlers.basic_file_handler import BasicFileHandler
from torch import Tensor

class ReplayMemoryManager():



    def __init__(self, capacity = 3000, batchSize=16) -> None:
        self.__fileHandler = BasicFileHandler("device-data.txt")
        data = self.__fileHandler.read()
        self.currentTransitionList:list[Transition] = []
        if data is None:
            self.replayMemory = ReplayMemory(capacity=capacity, batchSize=batchSize)
        else:
            self.replayMemory = ReplayMemory.fromDictList(data)

    def add(self, device:LoraDev, actionTaken:int, reward:float, energy:float, sleepTime:float) -> None:
        existingTransition = next((tran for tran in self.currentTransitionList if tran.id == device.deviceEUI), None)

        transition = Transition(device.deviceEUI, [energy, sleepTime], actionTaken, reward, device.time)
        self.currentTransitionList.append(transition)

        if existingTransition is not None:
            self.__inserTransition(existingTransition, energy, sleepTime)
            # self.currentTrainsitionList.remove(existingTransition)
            # existingTransition.addNextState([energy, sleepTime])
            # self.replayMemory.insert(existingTransition)

    def addEndOfDay(self, device:LoraDev, energy:float, sleepTime:float) -> None:
        existingTransition = next((tran for tran in self.currentTransitionList if tran.id == device.deviceEUI), None)

        if existingTransition is not None:
            self.__inserTransition(existingTransition, energy, sleepTime)
            # self.currentTrainsitionList.remove(existingTransition)
            # existingTransition.addNextState([energy, sleepTime])
            # self.replayMemory.insert(existingTransition)

    def addFailure(self, device:LoraDev) -> None:
        existingTransition = next((tran for tran in self.currentTransitionList if tran.id == device.deviceEUI), None)

        sleepTime = (device.oldSleepTime - QConstants.MAXIMUM_TS) - (QConstants.MAXIMUM_TS - QConstants.MINIMUM_TS)

        if existingTransition is not None:
            self.__inserTransition(existingTransition, float(0), sleepTime)
            # self.currentTrainsitionList.remove(existingTransition)
            # existingTransition.addNextState([float(0), sleepTime])
            # self.replayMemory.insert(existingTransition)
        
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
    
    def __inserTransition(self, transition: Transition, energy: float, sleepTime: float):
        data = [energy, sleepTime]
        
        self.currentTransitionList.remove(transition)
        transition.addNextState(data)
        self.replayMemory.insert(transition)

        self.__fileHandler.writeDict(transition.toStringDict())
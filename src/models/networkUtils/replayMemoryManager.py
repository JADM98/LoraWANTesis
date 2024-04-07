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

    def addEndOfDay(self, device:LoraDev, energy:float, sleepTime:float) -> None:
        existingTransition = next((tran for tran in self.currentTransitionList if tran.id == device.deviceEUI), None)

        if existingTransition is not None:
            self.__inserTransition(existingTransition, energy, sleepTime)

    def addFailure(self, device:LoraDev, actionTaken:int, reward:float, energy:float, sleepTime:float) -> None:
        existingTransition = next((tran for tran in self.currentTransitionList if tran.id == device.deviceEUI), None)

        tranition = Transition(device.deviceEUI, [energy, sleepTime], actionTaken, reward, device.time)
        self.currentTransitionList.append(tranition)

        if existingTransition is not None:
            #I think this is going to work since we set the sleep time last time the device transmitted.
            #Then we are up to date on it. Now we only have to create a new Transition with the newest info.
            self.__inserTransition(existingTransition, float(0), sleepTime)

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
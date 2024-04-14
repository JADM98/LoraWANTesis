from typing import List, Dict

from threading import Thread
from src.models.event import Event
from src.models.devices.loraDevice import LoraDevice, LoraDev
from src.models.queueManager.queueManager import LoraQueueManager
from src.models.secrets import Secrets
from src.models.networkUtils.networkManager import NetworkManager
from src.models.networkUtils.qNetworkConstants import QConstants
from src.models.file_handlers.basic_file_handler import BasicFileHandler

class EventProcessor():
    __fileHandler = BasicFileHandler("action-matrix.txt")
    devices:List[LoraDev] = []
    queueManager = LoraQueueManager(baseURL=Secrets.LORA_URL, 
        token=Secrets.TOKEN)
    neuralNetworkManager = NetworkManager(
        targetEnergy=QConstants.TARGET_ENERGY, replayMemoryBatchSize=QConstants.BATCH_SIZE,
        replayMemoryCapacity=QConstants.REPLAY_MEMORY_CAPACITY)

    @staticmethod
    def counter() -> int:
        return EventProcessor.neuralNetworkManager.counter
    
    @staticmethod
    def getLastEvent() -> Dict:
        return EventProcessor.neuralNetworkManager.getLastTransition()

    @staticmethod
    def evaluateState(battery:float, sleepTime:float) -> float:
        action = EventProcessor.neuralNetworkManager.evaluateWithNoTrain(battery, sleepTime)
        return action
    
    @staticmethod
    def getAction(battery:int, sleepTime:float) -> int:
        return EventProcessor.neuralNetworkManager.getActionWithNoTrain(battery, sleepTime)

    @staticmethod
    def process(event: Event):
        #Check if it exist in current list
        device = next((device for device in EventProcessor.devices if device.checkEUIMatch(event)), None)

        if device is None:
            device = LoraDevice(event)
            EventProcessor.devices.append(device)
        else:
            didUpdate = device.updateDevice(event)

            if not didUpdate:
                return device.sleepTime
        
        if device.isOk:
            state = EventProcessor.neuralNetworkManager.getNewSleepTime(device)
            # device.setNewSleepTime(sleepTime)
            # queueThread = Thread(target=EventProcessor.queueManager.enqueueSleepTime, 
            #                      args=[device, int( round( state.sleepTime/QConstants.STEP ) )])
            # queueThread.start()
            EventProcessor.neuralNetworkManager.processState(device, state)
        else:
            state = EventProcessor.neuralNetworkManager.getNewSleepTimeFromFailure(device)
            # device.setNewSleepTime(sleepTime)
            # queueThread = Thread(target=EventProcessor.queueManager.enqueueSleepTime, 
            #                      args=[device, int( round( state.sleepTime/QConstants.STEP ) )])
            # queueThread.start()
            EventProcessor.neuralNetworkManager.processFailure(device, state)

        device.setNewSleepTime(state.sleepTime)

        if EventProcessor.neuralNetworkManager.counter % 500 == 0 and EventProcessor.neuralNetworkManager.counter != 0:
            matrixTrhead = Thread(target=EventProcessor.__saveActionMatrix)
            matrixTrhead.start()
        
        return state.sleepTime
    
    @staticmethod
    def __saveActionMatrix():
        counter = str(EventProcessor.neuralNetworkManager.counter)

        batteries = [float(i / QConstants.MAXIMUM_BAT) for i in range(101)]
        sleepTimes = [float(i * QConstants.STEP / QConstants.MAXIMUM_TS) for i in range(int(30 / QConstants.STEP) + 1)]
        actions = []
        for i in range(len(batteries)):
            tempArray = []
            for j in range(len(sleepTimes)):
                action = EventProcessor.getAction(batteries[i], sleepTimes[j])
                tempArray.append(action)
            actions.append(tempArray)

        EventProcessor.__fileHandler.writeDict({
            counter: str(actions)
        })
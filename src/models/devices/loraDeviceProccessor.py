from src.models.event import Event
from src.models.devices.loraDevice import LoraDevice, LoraDev
from src.models.queueManager.queueManager import LoraQueueManager
from src.models.secrets import Secrets
from src.models.networkUtils.networkManager import NetworkManager
from src.models.networkUtils.qNetworkConstants import QConstants

class EventProcessor():
    devices:list[LoraDev] = []
    queueManager = LoraQueueManager(baseURL=Secrets.LORA_URL, 
        token=Secrets.TOKEN)
    neuralNetworkManager = NetworkManager(
        targetEnergy=QConstants.TARGET_ENERGY, replayMemoryBatchSize=QConstants.BATCH_SIZE,
        replayMemoryCapacity=QConstants.REPLAY_MEMORY_CAPACITY)

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
            sleepTime = device.sleepTime

            queueThread = Thread(target=EventProcessor.queueManager.enqueueSleepTime, args=[device, int(round(sleepTime/QConstants.STEP))])
            queueThread.start()

            EventProcessor.devices.append(device)
        else:
            didUpdate = device.updateDevice(event)

            if not didUpdate:
                return device.sleepTime
            if device.didRestart:
                device.setNewSleepTime(10)
                EventProcessor.neuralNetworkManager.replayMemoryManager.addFailure(device)
            if device.isPowered == False:
                EventProcessor.neuralNetworkManager.endDaySession(device=device)
                return QConstants.MAXIMUM_TS

            sleepTime = EventProcessor.neuralNetworkManager.processNewSleepTime(device=device)
            device.setNewSleepTime(sleepTime)
            

            #Post to LoRaWAN Gateway
            queueThread = Thread(target=EventProcessor.queueManager.enqueueSleepTime, args=[device, int(round(sleepTime/QConstants.STEP))])
            queueThread.start()

        return sleepTime
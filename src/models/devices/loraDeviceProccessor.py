from src.models.event import Event
from src.models.devices.loraDevice import LoraDevice, LoraDev
from src.models.queueManager.queueManager import LoraQueueManager
from src.models.secrets import Secrets
from src.models.networkUtils.networkManager import NetworkManager

from threading import Thread
import random

class EventProcessor():
    devices:list[LoraDev] = []
    queueManager = LoraQueueManager(baseURL=Secrets.LORA_URL, 
        token=Secrets.TOKEN)
    # neuralNetwork = NeuralNetwork()
    neuralNetworkManager = NetworkManager()
    # replayMemoryManager = ReplayMemoryManager()

    @staticmethod
    def process(event: Event):
        #Check if it exist in current list
        device = next((device for device in EventProcessor.devices if device.checkEUIMatch(event)), None)
        if device is None:
            device = LoraDevice(event)
            sleepTime = device.sleepTime

            queueThread = Thread(target=EventProcessor.queueManager.enqueueSleepTime, args=[device, sleepTime])
            queueThread.start()

            EventProcessor.devices.append(device)
        else:
            didUpdate = device.updateDevice(event)

            if not didUpdate:
                return 0
            # if device.didRestart:
            #     device.setNewSleepTime(10)

            sleepTime = EventProcessor.neuralNetworkManager.processNewSleepTime(device=device)
            device.setNewSleepTime(sleepTime)

            #Post to LoRaWAN Gateway
            queueThread = Thread(target=EventProcessor.queueManager.enqueueSleepTime, args=[device, sleepTime])
            queueThread.start()

        return sleepTime
from src.models.event import Event
from src.models.devices.loraDevice import LoraDeviceKalmanFiltered, LoraDevice, LoraDev
from src.models.kalmanFilter.simplifiedKalmanFilter import SimplifiedKalmanFilter
from src.models.queueManager.queueManager import LoraQueueManager
from src.models.secrets import Secrets
from src.models.networkUtils.networkManager import NetworkManager
from src.models.networkUtils.replayMemoryManager import ReplayMemoryManager

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
            # device = LoraDeviceKalmanFiltered(event)
            device = LoraDevice(event)
            sleepTime = device.sleepTime
            # device.setStdDevBattery(1.0)
            # device.setNoiseScalar(0.005)
            EventProcessor.devices.append(device)
        else:
            device.updateDevice(event)
            # if device.didRestart:
            #     device.setNewSleepTime(10)

            #Process battery in neural network
            # sleepTime = neuralNetwork.step(device.battery, device.sleepTime)
            sleepTime = EventProcessor.neuralNetworkManager.processNewSleepTime(device=device)

            if device.didRestart:
                print("Device was restarted, values set to: Battery = {}, SleepTime = {}, oldSleepTime = {}".format(
                    device.battery, device.sleepTime, device.oldSleepTime
                ))
            # sleepTime = device.sleepTime + random.randrange(-1, 2, 1)
            device.setNewSleepTime(sleepTime)

        #Post to LoRaWAN Gateway
        queueThread = Thread(target=EventProcessor.queueManager.enqueueSleepTime, args=[device, sleepTime])
        queueThread.start()
        queueThread.join()
        # print("Iteration: {}, Battery: {}, SleepTime: {}, oldSleepTime: {}, didRestart: {}".format(
        #     EventProcessor.neuralNetworkManager.counter, device.battery,device.sleepTime, device.oldSleepTime, device.didRestart))
        
        return sleepTime
        # pass

    
from src.models.event import Event
from src.models.devices.loraDevice import LoraDeviceKalmanFiltered, LoraDevice, LoraDev
from src.models.kalmanFilter.simplifiedKalmanFilter import SimplifiedKalmanFilter
from src.models.queueManager.queueManager import LoraQueueManager
from src.models.secrets import Secrets
from src.models.networkUtils.networkManager import NetworkManager
from src.models.networkUtils.replayMemoryManager import ReplayMemoryManager

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
        sleepTime = None
        device = next((device for device in EventProcessor.devices if device.checkEUIMatch(event)), None)
        if device is None:
            # device = LoraDeviceKalmanFiltered(event)
            device = LoraDevice(event)
            # device.setStdDevBattery(1.0)
            # device.setNoiseScalar(0.005)
            EventProcessor.devices.append(device)
        else:
            didUpdate = device.updateDevice(event)

            if not didUpdate:
                return 0
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
            EventProcessor.queueManager.enqueueSleepTime(device, sleepTime=sleepTime)
            # print("Iteration: {}, Battery: {}, SleepTime: {}, oldSleepTime: {}, didRestart: {}".format(
            #     EventProcessor.neuralNetworkManager.counter, device.battery,device.sleepTime, device.oldSleepTime, device.didRestart))
        
        return sleepTime
        # pass

    
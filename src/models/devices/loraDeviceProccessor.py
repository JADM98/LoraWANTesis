from models.event import Event
from models.devices.loraDevice import LoraDeviceKalmanFiltered, LoraDevice
from models.kalmanFilter.simplifiedKalmanFilter import SimplifiedKalmanFilter
from models.queueManager.queueManager import LoraQueueManager
from models.secrets import Secrets
from models.networkUtils.networkManager import NetworkManager
from models.networkUtils.replayMemoryManager import ReplayMemoryManager

import random

class EventProcessor():
    devices:list[LoraDeviceKalmanFiltered] = []
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
            device = LoraDeviceKalmanFiltered(event)
            device.setStdDevBattery(1.0)
            device.setNoiseScalar(0.005)
            EventProcessor.devices.append(device)
        else:
            device.updateDevice(event)
            # battery = device.battery

            #Process battery in neural network
            # sleepTime = neuralNetwork.step(device.battery, device.sleepTime)
            sleepTime = EventProcessor.neuralNetworkManager.processNewSleepTime(device=device)
            # sleepTime = device.sleepTime + random.randrange(-1, 2, 1)
            device.setNewSleepTime(sleepTime)

            #Post to LoRaWAN Gateway
            # EventProcessor.queueManager.enqueueSleepTime(device, sleepTime=sleepTime)
            print("Iteration: {}, Battery: {}, SleepTime: {}".format(
                EventProcessor.neuralNetworkManager.counter, device.battery,device.sleepTime))
        
        
        pass

    
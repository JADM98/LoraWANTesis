from models.event import Event
from models.devices.loraDevice import LoraDeviceKalmanFiltered, LoraDevice
from models.kalmanFilter.simplifiedKalmanFilter import SimplifiedKalmanFilter
from models.queueManager.queueManager import LoraQueueManager
from models.secrets import Secrets

import random

class EventProcessor():
    devices:list[LoraDeviceKalmanFiltered] = []
    queueManager = LoraQueueManager(Secrets.LORA_URL, 
        token=Secrets.TOKEN)

    @staticmethod
    def process(event: Event):
        #Check if it exist in current list
        device = next((device for device in EventProcessor.devices if device.checkEUIMatch(event)), None)
        if device is None:
            device = LoraDeviceKalmanFiltered(event)
            device.setStdDevBattery(2.0)
            device.setNoiseScalar(0.001)
            EventProcessor.devices.append(device)
        else:
            device.updateDevice(event)
            battery = device.battery

            #Process battery in neural network
            # sleepTime = neuralNetwork.step(battery, device.sleepTime)
            sleepTime = device.sleepTime + random.randrange(-1, 2, 1)
            device.setNewSleepTime(sleepTime)

            #Post to LoRaWAN Gateway
            EventProcessor.queueManager.enqueueSleepTime(device, sleepTime=sleepTime)

        
            # device.pre

        
        

        # #Calculate kalman filtered battery and next sleep time.
        # kalman = SimplifiedKalmanFilter()
        # kalman.setStandardDeviation(2)
        # kalman.setProcessNoiseScalar(0.0005)

        
        #Post the response in a method.
        
        pass

    
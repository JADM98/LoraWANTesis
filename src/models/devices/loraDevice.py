from models.event import Event
from models.decode import *
from models.kalmanFilter.simplifiedKalmanFilter import SimplifiedKalmanFilter
from abc import ABC, abstractmethod, abstractproperty

class LoraDev(ABC):
    @abstractproperty
    def deviceEUI(self):
        pass
    @abstractproperty
    def data(self):
        pass
    @abstractproperty
    def battery(self):
        pass
    @abstractproperty
    def sleepTime(self):
        pass
    @abstractmethod
    def checkEUIMatch(self, jsonEvent:Event) -> bool:
        pass
    @abstractmethod
    def updateDevice(self, jsonEvent:Event) -> bool:
        pass

class LoraDevice(LoraDev):

    @property
    def deviceEUI(self):
        return self.__devEui
    @property
    def data(self):
        return self.__data
    @property
    def battery(self):
        return self.__battery
    @property
    def sleepTime(self):
        return self.__sleepTime

    def __init__(self, jsonEvent:Event) -> None:
        self.__devEui = Decode.decode(jsonEvent.devEUI, decoder=Base64DecoderHex())
        self.__data = Decode.decode(jsonEvent.data, decoder=Base64DecoderUTF8())
        self.__battery = self.__data
        self.__sleepTime = 10

    def checkEUIMatch(self, jsonEvent:Event) -> bool:
        devEui = Decode.decode(data=jsonEvent.devEUI, decoder=Base64DecoderHex())
        return devEui == self.__devEui

    def updateDevice(self, jsonEvent:Event) -> bool:
        if self.checkEUIMatch(jsonEvent):
            self.__data = Decode.decode(jsonEvent.data, decoder=Base64DecoderUTF8())
            return True
        return False

    def setNewSleepTime(self, sleepTime:int) -> bool:
        if sleepTime <= 60 and sleepTime >= 1:
            self.__sleepTime = sleepTime
            return True
        return False

class LoraDeviceKalmanFiltered(LoraDev):
    @property
    def deviceEUI(self):
        return self.__devEui
    @property
    def data(self):
        return self.__data
    @property
    def battery(self):
        return self.__battery
    @property
    def sleepTime(self):
        return self.__sleepTime

    def __init__(self, jsonEvent: Event) -> None:
        self.__devEui = Decode.decode(jsonEvent.devEUI, decoder=Base64DecoderHex())
        self.__data = int(Decode.decode(jsonEvent.data, decoder=Base64DecoderInt()))
        self.__battery = self.__data
        self.__kalman = SimplifiedKalmanFilter()
        self.__sleepTime = 10   #minutes
        self.__kalman.setInitialValues(self.battery)
        print("Starting battery: {}".format(self.__battery))

    def checkEUIMatch(self, jsonEvent:Event) -> bool:
        devEui = Decode.decode(data=jsonEvent.devEUI, decoder=Base64DecoderHex())
        return devEui == self.__devEui

    def updateDevice(self, jsonEvent: Event) -> bool:
        if self.checkEUIMatch(jsonEvent):
            self.__data = int(Decode.decode(jsonEvent.data, decoder=Base64DecoderInt()))
            self.__kalman.predict()
            self.__battery = self.__kalman.update(self.__data)[0]
            self.__battery = 0 if self.__battery < 0 else self.__battery
            self.__battery = 100 if self.__battery > 100 else self.__battery
            # return float(self.__battery)
            return True
        return False
        
    def setStdDevBattery(self, stdDev: float):
        self.__kalman.setStandardDeviation(stdDev=stdDev)
    
    def setNoiseScalar(self, scalar:float):
        self.__kalman.setProcessNoiseScalar(scalar=scalar)
    
    def predictSteps(self, steps:int = 1):
        return self.__kalman.predictNSteps(steps)

    def setNewSleepTime(self, sleepTime:int) -> bool:
        if sleepTime <= 60 and sleepTime >= 1:
            self.__sleepTime = sleepTime
            self.__kalman.setNewMeasureTime(self.__sleepTime)
            return True
        return False

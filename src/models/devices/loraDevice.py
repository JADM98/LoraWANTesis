from src.models.event import Event
from src.models.decode import *
from src.models.kalmanFilter.simplifiedKalmanFilter import SimplifiedKalmanFilter
from abc import ABC, abstractmethod, abstractproperty
from src.models.eventUtils.loraDataParser import LoraDataParser

class LoraDev(ABC):
    @abstractproperty
    def deviceEUI(self) -> str:
        pass
    @abstractproperty
    def data(self) -> list[int]:
        pass
    @abstractproperty
    def battery(self) -> float:
        pass
    @abstractproperty
    def sleepTime(self) -> float:
        pass
    @abstractproperty
    def oldSleepTime(self) -> float:
        pass
    @abstractproperty
    def didRestart(self) -> bool:
        pass
    @abstractproperty
    def fPort(self) -> int:
        pass
    @abstractproperty
    def fCount(self) -> bool:
        pass
    @abstractmethod
    def checkEUIMatch(self, jsonEvent:Event) -> bool:
        pass
    @abstractmethod
    def updateDevice(self, jsonEvent:Event) -> bool:
        pass
    @abstractmethod
    def setNewSleepTime(self, sleepTime:int) -> bool:
        pass

class LoraDevice(LoraDev):

    @property
    def deviceEUI(self) -> str:
        return self.__devEui
    @property
    def data(self) -> list[int]:
        return self.__data
    @property
    def battery(self) -> float:
        return float(self.__battery)
    @property
    def sleepTime(self) -> float:
        return float(self.__sleepTime)
    @property
    def didRestart(self) -> bool:
        return self.__didRestart
    @property
    def oldSleepTime(self) -> float:
        return float(self.__oldSleepTime)
    @property
    def fPort(self) -> int:
        return self.__fPort
    @property
    def fCount(self) -> bool:
        return self.__fCount
    

    def __init__(self, jsonEvent:Event) -> None:
        decoder = DecoderFactory.create(DecoderFactory.BASE64_2_HEX)
        self.__devEui = decoder.decode(jsonEvent.devEUI)
        loraData = LoraDataParser(data=jsonEvent.data)
        self.__data = loraData.data
        self.__battery = loraData.battery
        self.__didRestart = loraData.didRestart
        self.__sleepTime = 10
        self.__oldSleepTime = 10
        self.__fPort = jsonEvent.fPort
        self.__fCount = jsonEvent.fCnt

    def checkEUIMatch(self, jsonEvent:Event) -> bool:
        decoder:str = DecoderFactory.create(DecoderFactory.BASE64_2_HEX)
        devEui = decoder.decode(jsonEvent.devEUI)
        return devEui == self.__devEui

    def updateDevice(self, jsonEvent:Event) -> bool:
        if self.checkEUIMatch(jsonEvent):

            if jsonEvent.fPort != 1:
                return False
            
            loraData = LoraDataParser(jsonEvent.data)
            self.__data = loraData.data
            self.__battery = loraData.battery
            self.__didRestart = loraData.didRestart
            self.__fCount = jsonEvent.fCnt
            if loraData.didRestart:
                self.setNewSleepTime(10)
                # self.__sleepTime = 10
            return True
        return False

    def setNewSleepTime(self, sleepTime:int) -> bool:
        if sleepTime <= 60 and sleepTime >= 1:
            self.__oldSleepTime = self.__sleepTime
            self.__sleepTime = sleepTime
            return True
        return False

class LoraDeviceKalmanFiltered(LoraDev):
    @property
    def deviceEUI(self) -> str:
        return self.__devEui
    @property
    def data(self) -> list[int]:
        return self.__data
    @property
    def battery(self) -> float:
        return float(self.__battery)
    @property
    def sleepTime(self) -> float:
        return float(self.__sleepTime)
    @property
    def didRestart(self) -> bool:
        return self.__didRestart
    @property
    def oldSleepTime(self) -> float:
        return float(self.__oldSleepTime)
    @property
    def fPort(self) -> int:
        return self.__fPort
    @property
    def fCount(self) -> bool:
        return self.__fCount

    def __init__(self, jsonEvent: Event) -> None:
        decoder = DecoderFactory.create(DecoderFactory.BASE64_2_HEX)
        self.__devEui = decoder.decode(jsonEvent.devEUI)
        loraData = LoraDataParser(jsonEvent.data)
        self.__data = loraData.data
        self.__battery = loraData.battery
        self.__didRestart = loraData.didRestart
        self.__kalman = SimplifiedKalmanFilter()
        self.__sleepTime = 10   #minutes
        self.__oldSleepTime = self.__sleepTime
        self.__kalman.setInitialValues(self.battery)
        self.__fPort = jsonEvent.fPort
        self.__fCount = jsonEvent.fCnt
        print("Starting battery: {}".format(self.__battery))

    def checkEUIMatch(self, jsonEvent:Event) -> bool:
        decoder = DecoderFactory.create(DecoderFactory.BASE64_2_HEX)
        devEui = decoder.decode(jsonEvent.devEUI)
        # devEui = Decoder.decode(data=jsonEvent.devEUI, decoder=Base64DecoderHex())
        return devEui == self.__devEui

    def updateDevice(self, jsonEvent: Event) -> bool:
        if self.checkEUIMatch(jsonEvent):
            if jsonEvent.fPort != 1:
                return False

            loraData = LoraDataParser(jsonEvent.data)
            self.__data = loraData.data
            self.__battery = loraData.battery
            self.__didRestart = loraData.didRestart
            if loraData.didRestart:
                self.__sleepTime = 10
                self.__kalman.setNewMeasureTime(self.__sleepTime)
                self.__kalman.setInitialValues(self.battery)
            else:
                self.__kalman.predict()
                self.__battery = self.__kalman.update(self.__battery)[0]
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
            self.__oldSleepTime = self.__sleepTime
            self.__sleepTime = sleepTime
            self.__kalman.setNewMeasureTime(self.__sleepTime)
            return True
        return False

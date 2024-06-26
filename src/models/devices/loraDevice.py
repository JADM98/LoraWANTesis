from typing import List

from src.models.event import Event
from src.models.decode import *
from src.models.kalmanFilter.simplifiedKalmanFilter import SimplifiedKalmanFilter
from abc import ABC, abstractmethod, abstractproperty
from src.models.eventUtils.loraDataParser import LoraDataParser
from src.models.networkUtils.qNetworkConstants import QConstants

class LoraDev(ABC):
    @abstractproperty
    def deviceEUI(self) -> str:
        pass
    @abstractproperty
    def data(self) -> List[int]:
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
    def lostPower(self) -> bool:
        pass
    @abstractproperty
    def isOk(self) -> bool:
        pass
    @abstractproperty
    def fPort(self) -> int:
        pass
    @abstractproperty
    def fCount(self) -> bool:
        pass
    @abstractproperty
    def time(self) -> str:
        pass
    @abstractmethod
    def checkEUIMatch(self, jsonEvent:Event) -> bool:
        pass
    @abstractmethod
    def updateDevice(self, jsonEvent:Event) -> bool:
        pass
    @abstractmethod
    def setNewSleepTime(self, sleepTime:float) -> bool:
        pass
    @abstractmethod
    def command(self) -> int:
        pass

class LoraDevice(LoraDev):

    @property
    def deviceEUI(self) -> str:
        return self.__devEui
    @property
    def data(self) -> List[int]:
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
    def lostPower(self) -> bool:
        return self.__lostPower
    @property
    def isOk(self) -> bool:
        return self.__isOk
    @property
    def oldSleepTime(self) -> float:
        return float(self.__oldSleepTime)
    @property
    def fPort(self) -> int:
        return self.__fPort
    @property
    def fCount(self) -> bool:
        return self.__fCount
    @property
    def command(self) -> int:
        return self.__command
    @property
    def time(self) -> str:
        return self.__time

    def __init__(self, jsonEvent:Event) -> None:
        decoder = DecoderFactory.create(DecoderFactory.BASE64_2_HEX)
        self.__devEui = decoder.decode(jsonEvent.devEUI)
        loraData = LoraDataParser(data=jsonEvent.data)
        self.__data = loraData.data
        self.__battery = loraData.battery
        self.__didRestart = loraData.didRestart
        self.__lostPower = loraData.lostPower
        self.__isOk = loraData.isOk
        self.__command = loraData.command
        self.__sleepTime = QConstants.INITIAL_SLEEP_TIME
        self.__oldSleepTime = QConstants.INITIAL_SLEEP_TIME
        self.__fPort = jsonEvent.fPort
        self.__fCount = jsonEvent.fCnt
        self.__time = jsonEvent.publishedAt

    def checkEUIMatch(self, jsonEvent:Event) -> bool:
        decoder:str = DecoderFactory.create(DecoderFactory.BASE64_2_HEX)
        devEui = decoder.decode(jsonEvent.devEUI)
        return devEui == self.__devEui

    def updateDevice(self, jsonEvent:Event) -> bool:
        if self.checkEUIMatch(jsonEvent):

            if jsonEvent.fPort != 1:
                return False
            
            loraData = LoraDataParser(jsonEvent.data)
            self.__command = loraData.command
            self.__didRestart = loraData.didRestart
            self.__lostPower = loraData.lostPower
            self.__isOk = loraData.isOk
            self.__data = loraData.data
            self.__fCount = jsonEvent.fCnt
            self.__battery = loraData.battery
            self.__time = jsonEvent.publishedAt
            self.__fPort = jsonEvent.fPort
            self.__fCount = jsonEvent.fCnt
            self.__oldSleepTime = self.__sleepTime

            return True
            # if not loraData.isOk:
            #     self.setNewSleepTime(5)
            #     return True
        return False

    def setNewSleepTime(self, sleepTime:float) -> bool:
        if sleepTime > QConstants.MAXIMUM_TS:
            sleepTime = QConstants.MAXIMUM_TS
        if sleepTime < QConstants.MINIMUM_TS:
            sleepTime = QConstants.MINIMUM_TS
        
        self.__oldSleepTime = self.__sleepTime
        self.__sleepTime = sleepTime
        return True

class LoraDeviceKalmanFiltered(LoraDev):
    @property
    def deviceEUI(self) -> str:
        return self.__devEui
    @property
    def data(self) -> List[int]:
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
    def lostPower(self) -> bool:
        return self.__lostPower
    @property
    def isOk(self) -> bool:
        return self.__isOk
    @property
    def oldSleepTime(self) -> float:
        return float(self.__oldSleepTime)
    @property
    def fPort(self) -> int:
        return self.__fPort
    @property
    def fCount(self) -> bool:
        return self.__fCount
    @property
    def time(self) -> str:
        return self.__time

    def __init__(self, jsonEvent: Event) -> None:
        decoder = DecoderFactory.create(DecoderFactory.BASE64_2_HEX)
        self.__devEui = decoder.decode(jsonEvent.devEUI)
        loraData = LoraDataParser(jsonEvent.data)
        self.__data = loraData.data
        self.__battery = loraData.battery
        self.__didRestart = loraData.didRestart
        self.__lostPower = loraData.lostPower
        self.__isOk = loraData.isOk
        self.__kalman = SimplifiedKalmanFilter()
        self.__sleepTime = QConstants.INITIAL_SLEEP_TIME   #minutes
        self.__oldSleepTime = self.__sleepTime
        self.__kalman.setInitialValues(self.battery)
        self.__fPort = jsonEvent.fPort
        self.__fCount = jsonEvent.fCnt
        self.__time = jsonEvent.publishedAt

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
            self.__lostPower = loraData.lostPower
            self.__isOk = loraData.isOk
            self.__time = jsonEvent.publishedAt
            self.__fCount = jsonEvent.fCnt
            self.__fPort = jsonEvent.fPort
            if loraData.didRestart:
                self.__sleepTime = QConstants.INITIAL_SLEEP_TIME
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

    def setNewSleepTime(self, sleepTime:float) -> bool:
        if sleepTime > QConstants.MAXIMUM_TS:
            sleepTime = QConstants.MAXIMUM_TS
        if sleepTime < QConstants.MINIMUM_TS:
            sleepTime = QConstants.MINIMUM_TS
        
        self.__oldSleepTime = self.__sleepTime
        self.__sleepTime = sleepTime
        return True

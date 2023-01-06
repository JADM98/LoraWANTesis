import requests
from base64 import b64encode
import models

class LoraQueueManager():
    def __init__(self, baseURL:str, token:str) -> None:
        self.__baseURL = baseURL.lower()
        if(self.__baseURL.find("http://") == -1):
            self.__baseURL = "http://" + self.__baseURL
        if(self.__baseURL.find("https://") == 0):
            self.__baseURL = "http://" + self.__baseURL[8:]
        self.__headers = {
            "Content-Type" : "application/json",
            "Authorization" : "Bearer " + token
        }


    def enqueueSleepTime(self, loraDevice: models.LoraDev, sleepTime: int):
        url = self.__baseURL + "/api/devices/" + loraDevice.deviceEUI + "/queue"
        data = b64encode(sleepTime.to_bytes(1, "big"))
        bodyDownlinkQueue = {
            "deviceQueueItem":{
                "confirmed" : False,
                "data" : data.decode(),
                "fPort": 1
            }
        }
        requests.post(url, json=bodyDownlinkQueue, headers=self.__headers)

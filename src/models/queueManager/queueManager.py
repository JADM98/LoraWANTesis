import requests
from base64 import b64encode
import src.models as models

class LoraQueueManager():
    def __init__(self, baseURL:str, token:str) -> None:
        self.__baseURL = baseURL.lower()
        if(self.__baseURL.find("http://") == -1):
            self.__baseURL = "http://" + self.__baseURL
        if(self.__baseURL.find("https://") == 0):
            self.__baseURL = "http://" + self.__baseURL[8:]
        if(self.__baseURL.endswith('/')):
            self.__baseURL = self.__baseURL[:-1]
        self.__headers = {
            "Content-Type" : "application/json",
            "Authorization" : "Bearer " + token
        }


    def enqueueSleepTime(self, loraDevice: models.LoraDev, sleepTime: int) -> requests.Response:
        url = self.__baseURL + "/api/devices/" + loraDevice.deviceEUI + "/queue"
        data = b64encode(sleepTime.to_bytes(1, "big"))
        bodyDownlinkQueue = {
            "deviceQueueItem":{
                "confirmed" : False,
                "data" : data.decode(),
                "fPort": 1
            }
        }
        return requests.post(url, json=bodyDownlinkQueue, headers=self.__headers)

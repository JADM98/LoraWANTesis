import os
import sys
sys.path.insert(0, os.getcwd())

from src import models

myDict = {"adr":True,"applicationID":"3","applicationName":"Tesis-App","confirmedUplink":False,"data":"AGQjfA==",
          "devAddr":"ACBaSg==","devEUI":"LE1IUv/aWVo=","deviceName":"MSP430FR5969-deJonathan",
          "deviceProfileID":"e66f54cf-4877-458d-be47-18697ccfedd3",
          "deviceProfileName":"MSP430-Beacons","dr":5,"fCnt":9746,"fPort":1,"objectJSON":"","publishedAt":"2022-12-23T20:51:17.143948793Z",
          "rxInfo":[{"antenna":0,"board":0,"channel":7,"context":"6suflA==","crcStatus":"CRC_OK","fineTimestampType":"NONE",
                     "gatewayID":"YMWo//52FO8=","loRaSNR":11,"location":{"accuracy":0,"altitude":0,"latitude":0,"longitude":0,
                            "source":"UNKNOWN"},"rfChain":1,"rssi":-40,"time":None,"timeSinceGPSEpoch":None,
                            "uplinkID":"i4wJFlNyRRy5d0GAWEhHiA=="}],"tags":{},"txInfo":{"frequency":868500000,"loRaModulationInfo":
                                    {"bandwidth":125,"codeRate":"4/5","polarizationInversion":False,"spreadingFactor":7},
                                    "modulation":"LORA"}}

myEv = models.Event.from_dict(myDict)

device = models.LoraDevice(myEv)

queueManager = models.LoraQueueManager(models.Secrets.LORA_URL, 
token=models.Secrets.TOKEN)
# print(device.deviceEUI)
response = queueManager.enqueueSleepTime(device, sleepTime=int(round(5/models.QConstants.STEP)))

print(response)

import os
import sys
sys.path.insert(0, os.getcwd())

from base64 import b64encode

from src import models

myDict = {"adr":True,"applicationID":"3","applicationName":"laboratory-testing","confirmedUplink":False,"data":"AGQjfA==","devAddr":"ALoO7g==","devEUI":"OxFijNhg9h4=","deviceName":"0001","deviceProfileID":"b5a2ae45-5904-4f3b-ab46-3fb3cac430c1","deviceProfileName":"Lab-Testing","dr":5,"fCnt":9746,"fPort":1,"objectJSON":"","publishedAt":"2022-12-23T20:51:17.143948793Z","rxInfo":[{"antenna":0,"board":0,"channel":7,"context":"6suflA==","crcStatus":"CRC_OK","fineTimestampType":"NONE","gatewayID":"YMWo//52FO8=","loRaSNR":11,"location":{"accuracy":0,"altitude":0,"latitude":0,"longitude":0,"source":"UNKNOWN"},"rfChain":1,"rssi":-40,"time":None,"timeSinceGPSEpoch":None,"uplinkID":"i4wJFlNyRRy5d0GAWEhHiA=="}],"tags":{},"txInfo":{"frequency":868500000,"loRaModulationInfo":{"bandwidth":125,"codeRate":"4/5","polarizationInversion":False,"spreadingFactor":7},"modulation":"LORA"}}

myEv = models.Event.from_dict(myDict)

device = models.LoraDeviceKalmanFiltered(myEv)
device.setStdDevBattery(2.1)
device.setNoiseScalar(0.0005)

for i in range(10):
    num = (0 + (75 - i*5)<<8)   #first 8 bits to command 0x00, next 8 bits correspond to battery level (0-100)
    data = b64encode(num.to_bytes(2, "little"))
    data = str(data)
    print(data)
    data = data[2:len(data)-1]

    myDict = {"adr":True,"applicationID":"3","applicationName":"laboratory-testing","confirmedUplink":False,"data":"{}".format(data),"devAddr":"ALoO7g==","devEUI":"OxFijNhg9h4=","deviceName":"0001","deviceProfileID":"b5a2ae45-5904-4f3b-ab46-3fb3cac430c1","deviceProfileName":"Lab-Testing","dr":5,"fCnt":9746,"fPort":1,"objectJSON":"","publishedAt":"2022-12-23T20:51:17.143948793Z","rxInfo":[{"antenna":0,"board":0,"channel":7,"context":"6suflA==","crcStatus":"CRC_OK","fineTimestampType":"NONE","gatewayID":"YMWo//52FO8=","loRaSNR":11,"location":{"accuracy":0,"altitude":0,"latitude":0,"longitude":0,"source":"UNKNOWN"},"rfChain":1,"rssi":-40,"time":None,"timeSinceGPSEpoch":None,"uplinkID":"i4wJFlNyRRy5d0GAWEhHiA=="}],"tags":{},"txInfo":{"frequency":868500000,"loRaModulationInfo":{"bandwidth":125,"codeRate":"4/5","polarizationInversion":False,"spreadingFactor":7},"modulation":"LORA"}}
    myEv = models.Event.from_dict(myDict)

    device.updateDevice(myEv)

    print("data: {}, battery:{}".format(device.data,device.battery))


print(device.predictSteps(5))

for i in range(10):
    num =  0 + ((30 + i*5) << 8)
    data = b64encode(num.to_bytes(2, "little"))
    data = str(data)
    data = data[2:len(data)-1]

    myDict = {"adr":True,"applicationID":"3","applicationName":"laboratory-testing","confirmedUplink":False,"data":"{}".format(data),"devAddr":"ALoO7g==","devEUI":"OxFijNhg9h4=","deviceName":"0001","deviceProfileID":"b5a2ae45-5904-4f3b-ab46-3fb3cac430c1","deviceProfileName":"Lab-Testing","dr":5,"fCnt":9746,"fPort":1,"objectJSON":"","publishedAt":"2022-12-23T20:51:17.143948793Z","rxInfo":[{"antenna":0,"board":0,"channel":7,"context":"6suflA==","crcStatus":"CRC_OK","fineTimestampType":"NONE","gatewayID":"YMWo//52FO8=","loRaSNR":11,"location":{"accuracy":0,"altitude":0,"latitude":0,"longitude":0,"source":"UNKNOWN"},"rfChain":1,"rssi":-40,"time":None,"timeSinceGPSEpoch":None,"uplinkID":"i4wJFlNyRRy5d0GAWEhHiA=="}],"tags":{},"txInfo":{"frequency":868500000,"loRaModulationInfo":{"bandwidth":125,"codeRate":"4/5","polarizationInversion":False,"spreadingFactor":7},"modulation":"LORA"}}
    myEv = models.Event.from_dict(myDict)

    device.updateDevice(myEv)

    print("data: {}, battery:{}".format(device.data,device.battery))

print(device.predictSteps(5))

# print("Device: {}, battery: {}".format(device.deviceEUI, device.battery))
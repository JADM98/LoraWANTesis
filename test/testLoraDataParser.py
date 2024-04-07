import os
import sys
sys.path.insert(0, os.getcwd())

from src import models


data = "AGQ=" #0x0064 = [0, 100]
loraData = models.LoraDataParser(data)
print(loraData.battery, loraData.isOk, loraData.didRestart, loraData.lostPower, loraData.command, loraData.data)

data = "AUA="
loraData = models.LoraDataParser(data)
print(loraData.battery, loraData.isOk, loraData.didRestart, loraData.lostPower, loraData.command, loraData.data)

data = "AlU="
loraData = models.LoraDataParser(data)
print(loraData.battery, loraData.isOk, loraData.didRestart, loraData.lostPower, loraData.command, loraData.data)


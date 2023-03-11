import os
import sys
sys.path.insert(0, os.getcwd())

from src import models


data = "AGQ=" #0x0064 = [0, 100]

loraData = models.LoraDataParser(data)

print(loraData.battery, loraData.didRestart, loraData.commandData, loraData.data)
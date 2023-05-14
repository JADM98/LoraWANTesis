from base64 import b64decode
from src.models.decode import DecoderFactory
import numpy as np

class LoraDataParser():

    def __init__(self, data:str) -> None:
        decoder = DecoderFactory.create(DecoderFactory.BASE64_2_INTHEXARRAY)
        intHexArray:list[int] = decoder.decode(data=data)

        self.command = intHexArray[0]
        self.battery = intHexArray[1]
        if len(intHexArray) >= 3:
            self.data = intHexArray[2:len(intHexArray)]
        else:
            self.data = []
        
        # self.didRestart = (self.command & 1) == 1
        self.didRestart = (self.command & 0x02) == 1
        self.isPowered = (self.command & 1) == 1
        self.commandData = self.command >> 1
from typing import List

from base64 import b64decode
from src.models.decode import DecoderFactory
import numpy as np

class LoraDataParser():

    def __init__(self, data:str) -> None:
        decoder = DecoderFactory.create(DecoderFactory.BASE64_2_INTHEXARRAY)
        intHexArray:List[int] = decoder.decode(data=data)

        self.command = intHexArray[0]
        self.battery = intHexArray[1]
        if len(intHexArray) >= 3:
            self.data = intHexArray[2:len(intHexArray)]
        else:
            self.data = []
        
        # self.didRestart = (self.command & 1) == 1
        # self.didRestart = (self.command & 0x02) == 1
        # self.isPowered = (self.command & 1) == 1
        # self.commandData = self.command >> 1
        self.didRestart = (self.command & Commands.RESET) == Commands.RESET
        self.isOk = (self.command & 0xFF) == Commands.OK
        self.lostPower = (self.command & Commands.DID_NOT_SENT) == Commands.DID_NOT_SENT

class Commands():
    OK = 0x00
    RESET = 0x01
    DID_NOT_SENT = 0x02
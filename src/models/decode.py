from base64 import b64decode
from abc import ABC, abstractmethod
from base64 import b64decode

class Decoder(ABC):
    @abstractmethod
    def decode(self, data:str) -> str:
        pass

class Decode():

    @staticmethod
    def decode(data:str, decoder:Decoder) -> str:
        return decoder.decode(data)

class DecoderFactory():

    HEX = 0
    UTF8 = 1
    INT = 2

    def create(decoder:int) -> Decoder:
        if decoder == DecoderFactory.HEX: return Base64DecoderHex()
        if decoder == DecoderFactory.UTF8: return Base64DecoderUTF8()
        if decoder == DecoderFactory.INT: return Base64DecoderInt()

class Base64DecoderHex(Decoder):
    def decode(self, data:str) -> str:
        return b64decode(data).hex()

class Base64DecoderUTF8(Decoder):
    def decode(self, data:str) -> str:
        return b64decode(data).decode('utf-8')

class Base64DecoderInt(Decoder):
    def decode(self, data:str) -> int:
        dataBytes = b64decode(data)
        return int.from_bytes(dataBytes, "big")


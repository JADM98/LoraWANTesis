from base64 import b64decode
from abc import ABC, abstractmethod
from base64 import b64decode

class Decoder(ABC):
    @abstractmethod
    def decode(self, data:str) -> str:
        pass

class Decode():

    @staticmethod
    def base64(data:str, decoder:Decoder) -> str:
        return decoder.decode(data)

class DecoderFactory():

    HEX = 0
    UTF8 = 1

    def create(decoder:int) -> Decoder:
        if decoder == DecoderFactory.HEX: return DecoderHex()
        if decoder == DecoderFactory.UTF8: return DecoderUTF8()

class DecoderHex(Decoder):
    def decode(self, data:str) -> str:
        return b64decode(data).hex()

class DecoderUTF8(Decoder):
    def decode(self, data:str) -> str:
        return b64decode(data).decode('utf-8')


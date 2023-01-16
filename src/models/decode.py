from base64 import b64decode
from abc import ABC, abstractmethod
from base64 import b64decode

class Decoder(ABC):
    @abstractmethod
    def decode(self, data:str) -> any:
        pass

# class Decode():

#     @staticmethod
#     def decode(data:str, decoder:Decoder) -> any:
#         return decoder.decode(data)

class DecoderFactory():

    BASE64_2_HEX = 0
    BASE64_2_UTF8 = 1
    BASE64_2_INT = 2
    BASE64_2_INTHEXARRAY = 3

    def create(decoder:int) -> Decoder:
        if decoder == DecoderFactory.BASE64_2_HEX: return Base64DecoderHex()
        if decoder == DecoderFactory.BASE64_2_UTF8: return Base64DecoderUTF8()
        if decoder == DecoderFactory.BASE64_2_INT: return Base64DecoderInt()
        if decoder == DecoderFactory.BASE64_2_INTHEXARRAY: return Base64DecoderIntHexArray()

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

class Base64DecoderIntHexArray(Decoder):
    def decode(self, data: str) -> list[int]:
        hexString = b64decode(data).hex()
        hexArray = bytes.fromhex(hexString)
        return [hexValue for hexValue in hexArray]




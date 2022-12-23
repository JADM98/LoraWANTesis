from models.event import Event
from models.decode import *

class LoraDevice():

    @property
    def deviceEUI(self):
        return self.__devEui
    @property
    def data(self):
        return self.__data

    def __init__(self, jsonEvent:Event) -> None:
        self.__devEui = Decode.base64(jsonEvent.devEUI, decoder=DecoderHex())
        self.__data = Decode.base64(jsonEvent.data, decoder=DecoderUTF8())
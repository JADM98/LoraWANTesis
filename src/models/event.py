# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = Eventfromdict(json.loads(json_string))

from dataclasses import dataclass
from typing import Any, List, TypeVar, Type, cast, Callable
from uuid import UUID
from datetime import datetime
import dateutil.parser


T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]



@dataclass
class RxInfo:
    channel: int
    crcStatus: str
    gatewayID: str
    loRaSNR: float
    rssi: int
    uplinkID: str

    @staticmethod
    def from_dict(obj: Any) -> 'RxInfo':
        assert isinstance(obj, dict)
        channel = from_int(obj.get("channel"))
        crcStatus = from_str(obj.get("crcStatus"))
        gatewayID = from_str(obj.get("gatewayID"))
        loRaSNR = from_float(obj.get("loRaSNR"))
        rssi = from_int(obj.get("rssi"))
        uplinkID = from_str(obj.get("uplinkID"))
        return RxInfo(channel, crcStatus, gatewayID, loRaSNR, rssi, uplinkID)


@dataclass
class LoRaModulationInfo:
    bandwidth: int
    codeRate: str
    polarizationInversion: bool
    spreadingFactor: int

    @staticmethod
    def from_dict(obj: Any) -> 'LoRaModulationInfo':
        assert isinstance(obj, dict)
        bandwidth = from_int(obj.get("bandwidth"))
        codeRate = from_str(obj.get("codeRate"))
        polarizationInversion = from_bool(obj.get("polarizationInversion"))
        spreadingFactor = from_int(obj.get("spreadingFactor"))
        return LoRaModulationInfo(bandwidth, codeRate, polarizationInversion, spreadingFactor)


@dataclass
class TxInfo:
    frequency: int
    loRaModulationInfo: LoRaModulationInfo
    modulation: str

    @staticmethod
    def from_dict(obj: Any) -> 'TxInfo':
        assert isinstance(obj, dict)
        frequency = from_int(obj.get("frequency"))
        loRaModulationInfo = LoRaModulationInfo.from_dict(obj.get("loRaModulationInfo"))
        modulation = from_str(obj.get("modulation"))
        return TxInfo(frequency, loRaModulationInfo, modulation)


@dataclass
class Event:
    adr: bool
    applicationID: int
    applicationName: str
    confirmedUplink: bool
    data: str
    devAddr: str
    devEUI: str
    deviceName: str
    deviceProfileID: UUID
    deviceProfileName: str
    dr: int
    fCnt: int
    fPort: int
    objectJSON: str
    publishedAt: datetime
    rxInfo: List[RxInfo]
    txInfo: TxInfo

    @staticmethod
    def from_dict(obj: Any) -> 'Event':
        assert isinstance(obj, dict)
        adr = from_bool(obj.get("adr"))
        applicationID = int(from_str(obj.get("applicationID")))
        applicationName = from_str(obj.get("applicationName"))
        confirmedUplink = from_bool(obj.get("confirmedUplink"))
        data = from_str(obj.get("data"))
        devAddr = from_str(obj.get("devAddr"))
        devEUI = from_str(obj.get("devEUI"))
        deviceName = from_str(obj.get("deviceName"))
        deviceProfileID = UUID(obj.get("deviceProfileID"))
        deviceProfileName = from_str(obj.get("deviceProfileName"))
        dr = from_int(obj.get("dr"))
        fCnt = from_int(obj.get("fCnt"))
        fPort = from_int(obj.get("fPort"))
        objectJSON = from_str(obj.get("objectJSON"))
        publishedAt = from_datetime(obj.get("publishedAt"))
        rxInfo = from_list(RxInfo.from_dict, obj.get("rxInfo"))
        txInfo = TxInfo.from_dict(obj.get("txInfo"))
        return Event(adr, applicationID, applicationName, confirmedUplink, data, devAddr, devEUI, deviceName, deviceProfileID, deviceProfileName, dr, fCnt, fPort, objectJSON, publishedAt, rxInfo, txInfo)
    
    def to_dict(self) -> dict:
        result: dict = {}
        result["adr"] = from_bool(self.adr)
        result["applicationID"] = from_str(str(self.applicationID))
        result["applicationName"] = from_str(self.applicationName)
        result["data"] = from_str(self.data)
        result["devAddr"] = from_str(self.devAddr)
        result["devEUI"] = from_str(self.devEUI)
        result["deviceName"] = from_str(self.deviceName)
        result["deviceProfileID"] = str(self.deviceProfileID)
        result["deviceProfileName"] = from_str(self.deviceProfileName)
        return result


def Eventfromdict(s: Any) -> Event:
    return Event.from_dict(s)
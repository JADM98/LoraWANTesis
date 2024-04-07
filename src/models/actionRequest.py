from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast


T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


@dataclass
class ActionRequest:
    battery: int
    sleepTime: float

    @staticmethod
    def from_dict(obj: Any) -> 'ActionRequest':
        assert isinstance(obj, dict)
        battery = from_int(obj.get("battery"))
        sleepTime = from_float(obj.get("sleepTime"))
        return ActionRequest(battery, sleepTime)
class ActionState():

    @property
    def action(self) -> int:
        return self.__action
    
    @property
    def sleepTime(self) -> float:
        return self.__sleepTime

    def __init__(self, sleepTime: float, action: int) -> None:
        self.__sleepTime = sleepTime
        self.__action = action
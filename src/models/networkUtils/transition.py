from typing import Dict, List

import ast

class Transition():
    #data is an array of 2 elements.
    #First element is energy and second is sleepTime
    def __init__(self, id:str, data:list[float], action:int, reward:float, time:str) -> None:
        self.id = id
        self.state = data
        self.action = action
        self.reward = reward
        self.time = time
        self.nextState:list = []
    
    @staticmethod
    def fromDict(data: Dict) -> 'Transition':

        state = ast.literal_eval(data["state"])
        action = int(data["action"])
        reward = float(data["reward"])
        nextState = ast.literal_eval(data["nextState"])

        transitionTemp = Transition(
            id=data["id"], data=state, action=action, reward=reward, time=data["time"])
        transitionTemp.addNextState(nextState)
        return transitionTemp

    def addNextState(self, data:List[float]):
        self.nextState = data

    def toList(self, showId=True) -> List[List]:
        myList = [self.state, [self.action], [self.reward], self.nextState]
        if showId:
            myList.insert(0, [self.id])
        return myList
    
    def toDict(self) -> Dict[str, any]:
        data = {
            "id": self.id,
            "state": self.state,
            "action": self.action,
            "reward": self.reward,
            "nextState": self.nextState,
            "time": self.time
        }

        return data
    
    def toStringDict(self) -> Dict[str, str]:
        data = {
            "id": self.id,
            "state": str(self.state),
            "action": str(self.action),
            "reward": str(self.reward),
            "nextState": str(self.nextState),
            "time": str(self.time)
        }

        return data
class Transition():
    def __init__(self, id:str, data:list, action:int, reward:float) -> None:
        self.id = id
        self.state = data
        self.action = action
        self.reward = reward
        self.nextState:list = []
    
    def addNextState(self, data:list):
        self.nextState = data

    def toList(self, showId=True) -> list[list]:
        myList = [self.state, [self.action], [self.reward], self.nextState]
        if showId:
            myList.insert(0, [self.id])
        return myList
import torch
import random
# import classes.transition as transition
from models.networkUtils.transition import Transition

class ReplayMemory():
    def __init__(self, capacity:int=3000, batchSize:int=32) -> None:
        self.capacity = capacity
        self.batch_size = batchSize
        self.memory:list[Transition] = []
        self.position = 0

    def insert(self, transition:Transition) -> None:
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        
        self.memory[self.position] = transition
        self.position = (self.position + 1) % self.capacity

    def sample(self) -> list[Transition]:
        assert self.can_sample()
        batch = random.sample(self.memory, self.batch_size)
        return batch

    def sampleList(self, showId=True) -> list[list[list]]:
        batch = self.sample()
        myList = [transition.toList(showId=showId) for transition in batch]
        return myList

    def sampleTensor(self) -> list[torch.Tensor]:
        assert self.can_sample()

        myList:list[torch.Tensor] = []
        for transitionElement in tuple(zip( *self.sampleList(showId=False) )):
            tensor = torch.cat([torch.tensor([e]) for e in transitionElement], dim=0)
            myList.append(tensor)
        return myList

    def getMemoryList(self) -> list[list[list]]:
        myList = [tran.toList() for tran in self.memory]
        return myList

    def can_sample(self):
        return len(self.memory) >= self.batch_size * 10

    def __len__(self):
        return len(self.memory)
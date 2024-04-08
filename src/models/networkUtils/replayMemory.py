from typing import List, Dict, Tuple

import torch
import random
# import classes.transition as transition
from src.models.networkUtils.transition import Transition
from src.models.networkUtils.qNetworkConstants import QConstants

class ReplayMemory():
    def __init__(self, capacity:int=3000, batchSize:int=32) -> None:
        self.capacity = capacity
        self.batch_size = batchSize
        self.memory:List[Transition] = []
        self.position = 0

    @staticmethod
    def fromDictList(data: List[dict[str, str]], capacity:int=3000, batchSize:int=32) -> 'ReplayMemory':
        replayMemory = ReplayMemory(capacity, batchSize)
        # replayMemory.memory = data
        replayMemory.memory = []
        for transitionData in data:
            transitionTemp = Transition.fromDict(transitionData)
            replayMemory.insert(transitionTemp)

        return replayMemory

    def insert(self, transition:Transition) -> None:
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        
        self.memory[self.position] = transition
        self.position = (self.position + 1) % self.capacity

    def sample(self) -> List[Transition]:
        assert self.can_sample()
        batch = random.sample(self.memory, self.batch_size)
        return batch

    def sampleList(self, showId=True) -> List[List[List]]:
        batch = self.sample()
        myList = [transition.toList(showId=showId) for transition in batch]
        return myList

    def sampleTensor(self) -> List[torch.Tensor]:
        assert self.can_sample()

        myList:List[torch.Tensor] = []
        for transitionElement in tuple(zip( *self.sampleList(showId=False) )):
            tensor = torch.cat([torch.tensor([e]) for e in transitionElement], dim=0)
            myList.append(tensor)
        return myList

    def getMemoryList(self) -> List[List[List]]:
        myList = [tran.toList() for tran in self.memory]
        return myList

    def can_sample(self):
        return len(self.memory) >= self.batch_size * QConstants.MINIMUM_TIMES_BS_TO_TRAIN

    def __len__(self):
        return len(self.memory)
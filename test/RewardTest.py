import os
import sys
sys.path.insert(0, os.getcwd())

from src import models

# energies = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
energies = [65, 80, 96]
targetEnergy = 80
sleepTimes = [i for i in range(1, 61)]

# models.RewardCalculator.calculate()

for energy in energies:
    for sleepTime in sleepTimes:
        for newSleepTime in [-10, -1, 0, 1, 10]:
            newSleepTime = sleepTime + newSleepTime
            if newSleepTime < 1:
                newSleepTime = 1
            if newSleepTime > 60:
                newSleepTime = 60

            reward = models.RewardCalculator.calculate(energy, targetEnergy, newSleepTime, sleepTime)

            print("Energy: {}, SleepTime: {}, newSleepTime: {}, Reward: {}".format(
                energy, sleepTime, newSleepTime, reward
            ))
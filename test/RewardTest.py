import os
import sys
sys.path.insert(0, os.getcwd())

from src import models

# energies = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
energies = [60, 80, 90]
targetEnergy = 80
sleepTimes = [i for i in [1, 10, 20, 30, 40, 50, 60]]

# models.RewardCalculator.calculate()

for energy in energies:
    for sleepTime in sleepTimes:
        for newSleepTime in [-10, -1, 0, 1, 10]:
            totalSleepTime = sleepTime + newSleepTime
            if totalSleepTime < 1:
                totalSleepTime = 1
            if totalSleepTime > 60:
                totalSleepTime = 60

            reward = models.RewardCalculator.calculate(energy, targetEnergy, newSleepTime, totalSleepTime)

            print("Energy: {}, SleepTime: {}, newSleepTime: {}, Reward: {}".format(
                energy, totalSleepTime, newSleepTime, reward
            ))
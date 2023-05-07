import os
import sys
sys.path.insert(0, os.getcwd())

from src import models

# energies = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
energies = [65, 75, 85, 95]
targetEnergy = 80
sleepTimes = [i for i in [0.25, 5, 10, 15, 20, 30]]

# models.RewardCalculator.calculate()

for energy in energies:
    for sleepTime in sleepTimes:
        for sleepTimeChange in [-5, -0.25, 0, 0.25, 5]:
            # totalSleepTime = sleepTime + newSleepTime
            # if totalSleepTime < 0.25:
            #     totalSleepTime = 0.25
            # if totalSleepTime > 30:
            #     totalSleepTime = 30

            reward = models.RewardCalculator.calculate(energy, targetEnergy, sleepTimeChange, sleepTime)

            print("Energy: {}, SleepTime: {}, newSleepTime: {}, Reward: {}".format(
                energy, sleepTime, sleepTimeChange, reward
            ))
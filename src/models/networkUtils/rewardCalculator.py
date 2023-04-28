import numpy as np

class RewardCalculator():

    @staticmethod
    def calculate(energy:int, targetEnergy:int, newSleepTime:int, oldSleepTime:int):

        # if didRestart: return float(-10)

        rewardEnergy = RewardCalculatorEnergyConservation.calculate(energy, targetEnergy, newSleepTime)
        rewardEnergy = RewardCalculatorEnergyConservation.adapt(
            rewardEnergy, energy, targetEnergy, newSleepTime)
        rewardTransmit = RewardCalculatorFastTransmission.calculate(newSleepTime + oldSleepTime)

        return rewardEnergy * 0.8 + rewardTransmit * 0.2

class RewardCalculatorEnergyConservation():

    @staticmethod
    def calculate(energy:int, targetEnergy:int, newSleepTime:int):
        #If new time is less
        energyDifference = energy - targetEnergy

        if newSleepTime < 0:
            if energyDifference > 10:
                reward = float(energyDifference/3 + 200/3)
            if energyDifference >= -10 and energyDifference <= 10:
                reward = float(0.07 * np.power(energyDifference, 3))
            if energyDifference < -10:
                reward = float(energyDifference/3 - 200/3)

        if newSleepTime == 0:
            if energyDifference >= -10 and energyDifference <= 10:
                reward = float(- np.power(energyDifference, 2) + 100)
            else:
                reward = float(-50)

        if newSleepTime > 0:
            if energyDifference > 10:
                reward = float(-energyDifference/3 - 200/3)
            if energyDifference >= -10 and energyDifference <= 10:
                reward = float(-0.07 * np.power(energyDifference, 3))
            if energyDifference < -10:
                reward = float(-energyDifference/3 + 200/3)
        
        return reward / 100

    @staticmethod
    def adapt(reward:float, energy:int, targetEnergy:int, newSleepTime:int):
        energy = energy - targetEnergy

        if energy < -15 or energy > 15:
            if newSleepTime == -1 or newSleepTime == 1:
                reward = reward * 0.75

        if energy > -15 and energy < 15:
            if newSleepTime == -10 or newSleepTime == 10:
                reward = reward * 0.85


        return reward

class RewardCalculatorFastTransmission():

    @staticmethod
    def calculate(newSleepTime):
        if newSleepTime < 1:
            newSleepTime = 1
        if newSleepTime > 60:
            newSleepTime = 60
        return float(np.power(0.942454, newSleepTime))
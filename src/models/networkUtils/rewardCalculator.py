import numpy as np
from src.models.networkUtils.qNetworkConstants import QConstants

class RewardCalculator():

    @staticmethod
    def calculate(energy:int, targetEnergy:int, sleepTimeChange:int, currentSleepTime:int):
        rewardEnergy = RewardCalculatorEnergyConservation.calculate(energy, targetEnergy, sleepTimeChange)
        rewardEnergy = RewardCalculatorEnergyConservation.adapt(
            rewardEnergy, energy, targetEnergy, sleepTimeChange)
        rewardTransmit = RewardCalculatorFastTransmission.calculate(2*(sleepTimeChange + currentSleepTime))

        return rewardEnergy * 0.8 + rewardTransmit * 0.2

class RewardCalculatorEnergyConservation():

    @staticmethod
    def calculate(energy:int, targetEnergy:int, sleepTimeChange:int):
        #If new time is less
        energyDifference = energy - targetEnergy

        if sleepTimeChange < 0:
            if energyDifference > 10:
                reward = float(energyDifference/3 + 200/3)
            if energyDifference >= -10 and energyDifference <= 10:
                reward = float(0.07 * np.power(energyDifference, 3))
            if energyDifference < -10:
                reward = float(energyDifference/3 - 200/3)

        if sleepTimeChange == 0:
            if energyDifference >= -10 and energyDifference <= 10:
                reward = float(- np.power(energyDifference, 2) + 100)
            else:
                reward = float(-100)

        if sleepTimeChange > 0:
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

        if energy <= -10 or energy >= 10:
            if newSleepTime == -QConstants.LOW_ACTION_CHANGE_VALUE or newSleepTime == QConstants.LOW_ACTION_CHANGE_VALUE:
                reward = reward * 0.60

        if energy > -10 and energy < 10:
            if newSleepTime == -QConstants.HIGH_ACTION_CHANGE_VALUE or newSleepTime == QConstants.HIGH_ACTION_CHANGE_VALUE:
                reward = reward * 0.60


        return reward

class RewardCalculatorFastTransmission():

    @staticmethod
    def calculate(newSleepTime):
        if newSleepTime < QConstants.MINIMUM_TS:
            newSleepTime = QConstants.MINIMUM_TS
        if newSleepTime > QConstants.MAXIMUM_TS:
            newSleepTime = QConstants.MAXIMUM_TS
        return float(np.power(0.942454, newSleepTime))
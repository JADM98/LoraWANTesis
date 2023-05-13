import numpy as np
from src.models.networkUtils.qNetworkConstants import QConstants

class RewardCalculator():

    @staticmethod
    def calculate(energy:int, targetEnergy:int, sleepTimeChange:int, currentSleepTime:int):
        rewardNewSleep = RewardCalculatorChangeSleep.calculate(energy, targetEnergy, sleepTimeChange)
        rewardAdapted = RewardCalculatorChangeSleep.adapt(
            rewardNewSleep, energy, targetEnergy, sleepTimeChange)
        rewardEnergy = RewardCalculatorEnergyObjective.calculate(energy, targetEnergy)

        reward = rewardEnergy + rewardAdapted
        return reward

class RewardCalculatorChangeSleep():

    @staticmethod
    def calculate(energy:int, targetEnergy:int, sleepTimeChange:int):
        #If new time is less
        energyDifference = energy - targetEnergy

        if sleepTimeChange > 0:
            reward = RewardCalculatorChangeSleep.function(energyDifference)

        elif sleepTimeChange == 0:
            if energyDifference >= -5 and energyDifference <= 5:
                reward = float(- 4 * np.power( energyDifference, 2) + 100)
            else:
                reward = float(-100)

        elif sleepTimeChange < 0:
            reward = RewardCalculatorChangeSleep.function(-energyDifference)
        
        return reward / 100

    @staticmethod
    def adapt(reward:float, energy:int, targetEnergy:int, newSleepTime:int):
        energy = energy - targetEnergy
        sleepTimeChange = np.absolute(newSleepTime)

        if energy <= -15 or energy >= 15:
            if sleepTimeChange == QConstants.LOW_ACTION_CHANGE_VALUE:
                if reward > 0:
                    reward *= 0
        if energy > -15 and energy < 15:
            if sleepTimeChange == QConstants.HIGH_ACTION_CHANGE_VALUE:
                if reward > 0:
                    reward *= 0
        return reward
    
    @staticmethod
    def function(energyDifference:float) -> float:
        if energyDifference < -10:
            return float(-energyDifference/3 + 200/3)
        else:
            return float( -370 / ( 1 + np.exp( -2*energyDifference ) ) + 70 )

class RewardCalculatorFastTransmission():

    @staticmethod
    def calculate(newSleepTime):
        if newSleepTime < QConstants.MINIMUM_TS:
            newSleepTime = QConstants.MINIMUM_TS
        if newSleepTime > QConstants.MAXIMUM_TS:
            newSleepTime = QConstants.MAXIMUM_TS
        return float(np.power(0.942454, newSleepTime))
    
class RewardCalculatorEnergyObjective():

    @staticmethod
    def calculate(energy:float, energyTarget:float) -> float:
        energyDifference = np.absolute(energy - energyTarget)

        if energyDifference <= 10:
            return float(1 - energyDifference * 0.1) 
        
        return float(0.0)
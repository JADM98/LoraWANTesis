import numpy as np
from src.models.networkUtils.qNetworkConstants import QConstants

class RewardCalculator():

    @staticmethod
    def calculate(energy:int, targetEnergy:int, sleepTimeChange:int, currentSleepTime:int):
        # rewardNewSleep = RewardCalculatorChangeSleep.calculate(energy, targetEnergy, sleepTimeChange)
        # rewardEnergy = RewardCalculatorEnergyObjective.calculate(energy, targetEnergy)
        # rewardTransmit = RewardCalculatorFastTransmission.calculate(2*(sleepTimeChange + currentSleepTime))
        # reward = rewardNewSleep * 0.8 + rewardTransmit * 0.2 + rewardEnergy
        # rewardAdapted = RewardCalculatorChangeSleep.adapt(
        #     reward, energy, targetEnergy, sleepTimeChange)
        rewardNewSleep = RewardCalculatorChangeSleep.calculate(energy, targetEnergy, sleepTimeChange)
        rewardNewSleep = RewardCalculatorChangeSleep.adapt(rewardNewSleep, energy, targetEnergy, sleepTimeChange)
        rewardEnergy = RewardCalculatorEnergyObjective.calculate(energy, targetEnergy)
        # rewardTransmit = RewardCalculatorFastTransmission.calculate(2*(sleepTimeChange + currentSleepTime))

        reward = rewardNewSleep + rewardEnergy
        return reward

class RewardCalculatorChangeSleep():

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
            if energyDifference >= -5 and energyDifference <= 5:
                reward = float(- np.power( 8 * energyDifference, 2) + 100)
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

        if energy <= -15 or energy >= 15:
            if newSleepTime == -QConstants.LOW_ACTION_CHANGE_VALUE or newSleepTime == QConstants.LOW_ACTION_CHANGE_VALUE:
                if reward > 0:
                    reward = 0
                else:
                    reward *= 1.5
        if energy > -15 and energy < 15:
            if newSleepTime == -QConstants.HIGH_ACTION_CHANGE_VALUE or newSleepTime == QConstants.HIGH_ACTION_CHANGE_VALUE:
                if reward > 0:
                    reward = 0
                else: 
                    reward *= 1.5

        return reward

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
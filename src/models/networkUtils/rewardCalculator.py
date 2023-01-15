import numpy as np

class RewardCalculator():

    @staticmethod
    def calculate(energy:int, targetEnergy:int, newSleepTime:int):
        rewardEnergy = RewardCalculatorEnergyConservation.calculate(energy, targetEnergy, newSleepTime)
        rewardTransmit = RewardCalculatorFastTransmission.calculate(newSleepTime)

        return rewardEnergy * 0.8 + rewardTransmit * 0.2

class RewardCalculatorEnergyConservation():

    @staticmethod
    def calculate(energy:int, targetEnergy:int, newSleepTime:int):
        if newSleepTime < 0:
            energy = targetEnergy - energy
            if energy < -10:
                reward = float(-energy/3 + 200/3)
            if energy >= -10 and energy <= 10:
                reward = float(-0.07 * np.power(energy, 3))
            if energy > 10:
                reward = float(-energy/3 - 200/3)

        if newSleepTime == 0:
            energy = targetEnergy - energy
            if energy >= -10 and energy <= 10:
                reward = float(- np.power(energy, 2) + 100)
            else:
                reward = float(-50)

        if newSleepTime > 0:
            energy = targetEnergy - energy
            if energy < -10:
                reward = float(energy/3 - 200/3)
            if energy >= -10 and energy <= 10:
                reward = float(0.07 * np.power(energy, 3))
            if energy > 10:
                reward = float(energy/3 + 200/3)
        
        return reward / 100

class RewardCalculatorFastTransmission():

    @staticmethod
    def calculate(newSleepTime):
        return float(np.power(0.942454, newSleepTime))
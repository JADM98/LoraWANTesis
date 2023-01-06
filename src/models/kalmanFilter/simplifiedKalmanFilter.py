from typing import Tuple
import warnings
import numpy as np

class SimplifiedKalmanFilter():
    
    def __init__(self, numberOfVariables:int=1, secondsToMeasure:float=1, includeVelocity:bool=True) -> None:
        if numberOfVariables < 1:
            raise ValueError("Number of variables must be 1 or Higher.")
        
        self.numberOfVariables = numberOfVariables
        self.includeVelocity = includeVelocity
        self.sizeOfMatrix = self.numberOfVariables * (1+self.includeVelocity)

        self.X = np.zeros( (self.sizeOfMatrix, 1), dtype=np.float64)
        self.F = np.zeros((self.sizeOfMatrix, self.sizeOfMatrix), dtype=np.float64)     #Transition Matrix
        self.H = np.zeros((self.numberOfVariables, self.sizeOfMatrix ))                 #Observation Matrix            

        self.B = 0                                                                      #Control Matrix
        self.Q = 0.01 * np.eye( self.sizeOfMatrix )                                            #Process Noise Matrix
        self.R = np.eye( self.numberOfVariables )                                       #Measurement Noise Matrix
        self.P = np.eye( self.sizeOfMatrix )                                            #Process cov Matrix
        
        for i in range(self.numberOfVariables):
            self.F[i, i] = 1
            self.H[i, i] = 1
            if self.includeVelocity:
                self.F[i+self.numberOfVariables, i+self.numberOfVariables] = 1
                self.F[i, i+self.numberOfVariables] = 1/secondsToMeasure

    def setStandardDeviation(self, stdDev:list[int]|Tuple[int]|np.ndarray|float):
        isInstance, stdDev = self.__checkDataInstace(stdDev)
        if isInstance:
            for i in range(self.numberOfVariables):
                self.R[i,i] = stdDev[i]

    def setProcessNoiseScalar(self, scalar:int|float):
        if scalar < 0:
            raise ValueError("Scalar of Q matrix cannot be negative.")
        if scalar == 0:
            warnings.warn("Process Noise scalar should not be 0, giving a positive value helps the model (try 0.005).")
        self.Q = scalar * np.eye( self.sizeOfMatrix ) 

    def setNewMeasureTime(self, time:list[int]|Tuple[int]|np.ndarray|float):
        isInstance, time = self.__checkDataInstace(time)
        if isInstance:
            for i in range(self.numberOfVariables):
                self.F[i, i+self.numberOfVariables] = 1/time[i]
        
    def predict(self, u = 0) -> Tuple[float, ...]:
        self.X = np.dot(self.F, self.X) + np.dot(self.B, u)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        return tuple([float(var) for var in np.dot(self.H, self.X)])

    def predictNSteps(self, steps:int) -> Tuple[float, ...]:
        if steps < 1:
            raise ValueError("Number of steps should be 1 or higher")
        predictions = []
        predictedX = np.dot(self.F, self.X)
        value = np.dot(self.H, predictedX)
        predictions.append(tuple([float(value)]))
        for _ in range(steps - 1):
            predictedX = np.dot(self.F, predictedX)
            value = np.dot(self.H, predictedX)
            predictions.append(tuple([float(value)]))
            
        return tuple(predictions)

    def update(self, z:list[int]|Tuple[int]|np.ndarray|float) -> Tuple[float, ...]:
        isIstance, z = self.__checkDataInstace(z)
        if isIstance:
            y = z - np.dot(self.H, self.X)
            S = self.R + np.dot(self.H, np.dot(self.P, self.H.T))
            K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
            self.X = self.X + np.dot(K, y)
            I = np.eye( self.numberOfVariables* (1+self.includeVelocity) )
            self.P = np.dot(I - np.dot(K, self.H), self.P)

        return tuple([float(np.dot(self.H, self.X))])

    def __checkDataInstace(self, myData):
        if isinstance(myData, int) or isinstance(myData, float):
            myData = (myData,)

        if isinstance(myData, Tuple) or isinstance(myData, list) or isinstance(myData, np.ndarray):
            myData = np.array(myData)
            if len(myData) is not self.numberOfVariables:
                raise ValueError("Cannot assign values because the expected size of the array was: {}, however the length was: {}".format(self.numberOfVariables, len(myData)))
            else:
                return True, myData
        else:
            raise ValueError("Cannot operate object of type {}, the expected type is float, tuple, list or np.ndarray".format(type(myData)))

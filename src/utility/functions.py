from typing import Callable

class LambdaUtils:
    __counter=0

    @staticmethod
    def isLambda(function:Callable) -> bool:
        return function.__name__ == (lambda:0).__name__

    @staticmethod
    def createNamedLambda(function:Callable) -> Callable:
        function.__name__ = "lambda{}".format(LambdaUtils.__counter)
        LambdaUtils.__increaseCounter()
        return function

    @staticmethod
    def __increaseCounter() -> None:
        LambdaUtils.__counter += 1
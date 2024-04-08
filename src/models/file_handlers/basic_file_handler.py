from typing import Dict, List, Union

import os
import threading

class BasicFileHandler():

    def __init__(self, fileName : str) -> None:
        self.__fileName = fileName
        if not os.path.isfile(self.__fileName):
            file = open(self.__fileName, 'x')
            file.close()

    def writeDict(self, data: Dict[str, str]) -> None:

        with open(self.__fileName, 'a') as file:
            stringTemp = ""
            for key, value in data.items():
                stringTemp += key + "=" + value + "|"
            stringTemp = stringTemp[:-1]
            stringTemp += "\n"
            
            file.write(stringTemp)

    def readLastLine(self) -> Union[Dict[str, str], None]:
        line = None
        data = None

        # FileLocks.acquire(self.__fileName)

        with open(self.__fileName, 'r') as file:
            line = file.readline()

        # FileLocks.release(self.__fileName)

        if line is not None and line != '':
            data = self.__parseLineIntoData(line)

        return data

    def read(self) -> Union[List[Dict[str, str]] | None]:
        lines = []

        # FileLocks.acquire(self.__fileName)

        with open(self.__fileName, 'r') as file:
            line = file.readline()
            while line is not None and line != '':
                lines.append(line)
                line = file.readline()

        # FileLocks.acquire(self.__fileName)

        data = []
        for lineTemp in lines:
            dataTemp = self.__parseLineIntoData(lineTemp)
            data.append(dataTemp)

        return data if len(data) > 0 else None

            
    def __parseLineIntoData(self, line: str) -> Dict:
        lines = line.split("|")
        data = {}
        for valuesString in lines:
            values = valuesString.split("=")
            key = values[0].strip()
            value = values[1].strip()
            data[key] = value

        return data
    
    # def __writeHandler(self, data: dict[str, str]):
        
    #     FileLocks.acquire(self.__fileName)

    #     with open(self.__fileName, 'a') as file:
    #         stringTemp = ""
    #         for key, value in data.items():
    #             stringTemp += key + "=" + value + "|"
    #         stringTemp = stringTemp[:-1]
    #         stringTemp += "\n"
            
    #         file.write(stringTemp)

    #     FileLocks.release(self.__fileName)

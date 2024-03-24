class BasicFileHandler():

    def __init__(self, fileName : str) -> None:
        self.__fileName = fileName

    def writeDict(self, data: dict[str, str]) -> None:
        with open(self.__fileName, 'a') as file:
            stringTemp = ""
            for key, value in data.items():
                stringTemp += key + "=" + value + "|"
            stringTemp = stringTemp[:-1]
            stringTemp += "\n"
            
            file.write(stringTemp)

    def readLastLine(self) -> dict[str, str] | None:
        line = None
        data = None
        with open(self.__fileName, 'r') as file:
            line = file.readline()

        if line is not None and line != '':
            data = self.__parseLineIntoData(line)

        return data

    def read(self) -> list[dict[str, str]] | None:
        lines = []

        with open(self.__fileName, 'r') as file:
            line = file.readline()
            while line is not None and line != '':
                lines.append(line)
                line = file.readline()

        data = []
        for lineTemp in lines:
            dataTemp = self.__parseLineIntoData(lineTemp)
            data.append(dataTemp)

        return data if len(data) > 0 else None

            
    def __parseLineIntoData(self, line: str) -> dict:
        lines = line.split("|")
        data = {}
        for valuesString in lines:
            values = valuesString.split("=")
            key = values[0].strip()
            value = values[1].strip()
            data[key] = value

        return data

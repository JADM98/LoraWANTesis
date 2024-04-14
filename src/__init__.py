from flask import Flask, jsonify, request, send_file
import src.models as models
import numpy as np

app = Flask(__name__)

def getLossFile():
    return send_file("../loss-data.txt", as_attachment=True)

def getDeviceDataFile():
    return send_file("../device-data.txt", as_attachment=True)

def getModelFile():
    return send_file("../model.pth", as_attachment=True)

def getMatrixFile():
    return send_file("../action-matrix.txt", as_attachment=True)

def handleTest():
    global myJson
    if request.is_json:
        myJson = models.Event.from_dict(request.json)
        sleepTime = models.EventProcessor.process(event=myJson)    #We cast floating to int 0.25 -> 1, 30 -> 120
        sleepTime = int(sleepTime / models.QConstants.STEP)
        return jsonify({"sleepTime":sleepTime})
    
    return jsonify({"message":"Rejected, body was not a json"})

def getLoss():
    array:np.ndarray = models.EventProcessor.neuralNetworkManager.loss
    return jsonify(array.tolist())

def getAction():
    if request.is_json:
        myJson = models.ActionRequest.from_dict(request.json)
        battery = (myJson.battery - models.QConstants.MINIMUM_BAT) / (models.QConstants.MAXIMUM_BAT - models.QConstants.MINIMUM_BAT)
        sleepTime = (myJson.sleepTime - models.QConstants.MINIMUM_TS) / (models.QConstants.MAXIMUM_TS - models.QConstants.MINIMUM_TS)
        action = models.EventProcessor.evaluateState(battery, sleepTime)
        return jsonify({"actionTaken":action})
    
    return jsonify({"message":"Rejected, body was not a json"})

def getActionMatrix():
    batteries = [float(i / models.QConstants.MAXIMUM_BAT) for i in range(101)]
    sleepTimes = [float(i*models.QConstants.STEP / models.QConstants.MAXIMUM_TS) for i in range(int(30 / models.QConstants.STEP) + 1)]
    actions = []
    for i in range(len(batteries)):
        tempArray = []
        for j in range(len(sleepTimes)):
            action = models.EventProcessor.getAction(batteries[i], sleepTimes[j])
            tempArray.append(action)
        actions.append(tempArray)

    return jsonify(actions)

def getTest():
    return jsonify(myJson.to_dict())

def getAll():
    return jsonify(models.EventProcessor.neuralNetworkManager.replayMemoryManager.getMemory())

def returnOk():
    return jsonify({"message":"Ok"})

def returnHello():
    return "This ain't the page you're looking for, but is good to see you here"

def counter():
    return jsonify({"count": models.EventProcessor.counter()})
        
models.Routes.addRoute(app=app, url="/device", function=handleTest, methods=models.RouteMethods.POST)
models.Routes.addRoute(app=app, url="/device", function=getTest)
models.Routes.addRoute(app=app, url="/evaluate/action", function=getAction)
models.Routes.addRoute(app=app, url="/evaluate/model", function=getActionMatrix)
models.Routes.addRoute(app=app, url="/memory", function=getAll)
models.Routes.addRoute(app=app, url="/loss", function=getLoss)
models.Routes.addRoute(app=app, url="/test", function=returnOk)
models.Routes.addRoute(app=app, url="/", function=returnHello)
models.Routes.addRoute(app=app, url="/files/model", function=getModelFile)
models.Routes.addRoute(app=app, url="/files/loss", function=getLossFile)
models.Routes.addRoute(app=app, url="/files/device-data", function=getDeviceDataFile)
models.Routes.addRoute(app=app, url="/files/action-matrix", function=getMatrixFile)
models.Routes.addRoute(app=app, url="/count", function=counter)
models.Routes.addRoute(app=app, url="/memory/last", function=models.EventProcessor.getLastEvent)
from flask import Flask, jsonify, request
import src.models as models
from concurrent import futures

app = Flask(__name__)
threadPool = futures.ThreadPoolExecutor(max_workers=4)

def handleTest():
    global myJson
    if request.is_json:
        myJson = models.Event.from_dict(request.json)
        sleepTime = models.EventProcessor.process(event=myJson)
        return jsonify({"sleepTime":sleepTime})
    
    return jsonify({"message":"Rejected, body was not a json"})

def getTest():
    return jsonify(myJson.to_dict())

def getAll():
    return jsonify(models.EventProcessor.neuralNetworkManager.replayMemoryManager.getMemory())

def returnOk():
    return jsonify({"message":"Ok"})

def returnHello():
    return "This ain't the page you're looking for, but is good to see you here"
        
models.Routes.addRoute(app=app, url="/device", function=handleTest, methods=models.RouteMethods.POST)
models.Routes.addRoute(app=app, url="/device", function=getTest)
models.Routes.addRoute(app=app, url="/memory", function=getAll)
models.Routes.addRoute(app=app, url="/test", function=returnOk)
models.Routes.addRoute(app=app, url="/", function=returnHello)
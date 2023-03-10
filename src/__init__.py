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
    if models.EventProcessor.neuralNetworkManager.replayMemoryManager.canSample():
        return jsonify(models.EventProcessor.neuralNetworkManager.replayMemoryManager.sampleList())
    
    return jsonify([])

def getAll():
    return jsonify(models.EventProcessor.neuralNetworkManager.replayMemoryManager.getMemory())
        
models.Routes.addRoute(app=app, url="/info", function=handleTest, methods=models.RouteMethods.POST)
models.Routes.addRoute(app=app, url="/info", function=getTest)
models.Routes.addRoute(app=app, url="/memory", function=getAll)
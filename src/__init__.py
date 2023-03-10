from flask import Flask, jsonify, request
import src.models as models
from concurrent import futures

device: models.LoraDevice
app = Flask(__name__)
threadPool = futures.ThreadPoolExecutor(max_workers=4)

def handleTest():
    # global myJson
    global device
    if request.is_json:
        myJson = models.Event.from_dict(request.json)
        # device = models.LoraDevice(myJson)
        # models.EventProcessor.process(device=device)
        sleepTime = models.EventProcessor.process(event=myJson)
        return jsonify({"sleepTime":sleepTime})
    
    return jsonify({"message":"Rejected, body was not a json"})

def getTest():
    # return jsonify({"message":jsonResponse})
    # return jsonify(myJson.to_dict())
    # dec = DecoderFactory.create(DecoderFactory.UTF8)
    # data = models.Decode.base64(data=device., decoder=models.DecoderUTF8())
    # return jsonify({"data":device.data})
    if models.EventProcessor.neuralNetworkManager.replayMemoryManager.canSample():
        return jsonify(models.EventProcessor.neuralNetworkManager.replayMemoryManager.sampleList())
    
    return jsonify([])

def getAll():
    return jsonify(models.EventProcessor.neuralNetworkManager.replayMemoryManager.getMemory())
        


# Routes.addRoute(app=app, url="/test", function=lambda:jsonify({"message":"Ok"}))
# Routes.addRoute(app=app, url="/test1", function=lambda:jsonify({"message":"Not Ok"}))
# Routes.addRoute(app=app, url="/test2", function=lambda:jsonify({"message":"So so"}))
models.Routes.addRoute(app=app, url="/test3", function=handleTest, methods=models.RouteMethods.POST)
models.Routes.addRoute(app=app, url="/test3", function=getTest)
models.Routes.addRoute(app=app, url="/memory", function=getAll)

if __name__ == '__main__':
    app.run(debug=False, port=4000)
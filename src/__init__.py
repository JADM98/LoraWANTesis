from flask import Flask, jsonify, request
from src import models
from concurrent import futures

device: models.LoraDevice
app = Flask(__name__)
threadPool = futures.ThreadPoolExecutor(max_workers=4)

def handleTest():
    # global myJson
    global myJson
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
    # return jsonify({"devEUI":device.deviceEUI, "data":device.data, "sleepTime":device.sleepTime})
    return jsonify(myJson.to_dict())
    # if models.EventProcessor.neuralNetworkManager.replayMemoryManager.canSample():
    #     return jsonify(models.EventProcessor.neuralNetworkManager.replayMemoryManager.sampleList())
    
    return jsonify([])

def getAll():
    return jsonify(models.EventProcessor.neuralNetworkManager.replayMemoryManager.getMemory())
        
def getDevices():
    devs = models.EventProcessor.devices
    list1 = []

    for dev in devs:
        devDict = {"devEUI": dev.deviceEUI, "data":dev.data, "sleepTime":dev.sleepTime}
        list1.append(devDict)

    return jsonify(list1)


models.Routes.addRoute(app=app, url="/test3", function=handleTest, methods=models.RouteMethods.POST)
models.Routes.addRoute(app=app, url="/test3", function=getTest)
models.Routes.addRoute(app=app, url="/memory", function=getAll)

if __name__ == '__main__':
    app.run(debug=False, port=4000)
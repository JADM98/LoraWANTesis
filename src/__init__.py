from flask import Flask, jsonify, request
import models
# from concurrent import futures
app = Flask(__name__)
# threadPool = futures.ThreadPoolExecutor(max_workers=4)
# jsonResponse:str = ""
# myJson:Event
myJson: models.Event

def handleTest():
    global myJson
    if request.is_json:
        myJson = models.Event.from_dict(request.json)
        device = models.LoraDevice(myJson)
        print(device.data)
        print(device.deviceEUI)
        # print(dev1)
        return jsonify({"message":"Accepted"})
    
    return jsonify({"message":"Rejected, body was not a json"})

def getTest():
    # return jsonify({"message":jsonResponse})
    # return jsonify(myJson.to_dict())
    # dec = DecoderFactory.create(DecoderFactory.UTF8)
    data = models.Decode.base64(data=myJson.data, decoder=models.DecoderUTF8())
    return jsonify({"data":data})


# Routes.addRoute(app=app, url="/test", function=lambda:jsonify({"message":"Ok"}))
# Routes.addRoute(app=app, url="/test1", function=lambda:jsonify({"message":"Not Ok"}))
# Routes.addRoute(app=app, url="/test2", function=lambda:jsonify({"message":"So so"}))
models.Routes.addRoute(app=app, url="/test3", function=handleTest, methods=models.RouteMethods.POST)
models.Routes.addRoute(app=app, url="/test3", function=getTest)

if __name__ == '__main__':
    app.run(debug=False, port=4000)
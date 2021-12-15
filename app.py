from wsgiref import simple_server
from flask import Flask, request, Response
from flask_cors import CORS
from flask import render_template, redirect, url_for, send_from_directory, send_file
from flask_cors import cross_origin
import json
from getNumberPlateVals import detect_license_plate
import base64
import os
from predict_images import DetectVehicleNumberPlate

application = Flask(__name__)

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')
CORS(application)

inputFileName = "inputImage.jpg"
imagePath = "Prediction_InputFileFromUser/" + inputFileName
image_display = True
pred_stagesArgVal = 2
croppedImagepath = "images/croppedImage.jpg"

application.config["sample_file"] = "Prediction_SampleFile/"

@application.route('/')
@cross_origin()
def home():
    return render_template('index.html')

@application.route('/return_sample_file/')
@cross_origin()
def return_sample_file():
    sample_file = os.listdir("Prediction_SampleFile/")[0]
    return send_from_directory(application.config["sample_file"], sample_file)



class ClientApp:
    def __init__(self):
        # modelArg = "datasets/experiment_faster_rcnn/2018_08_02/exported_model/frozen_inference_graph.pb"
        self.modelArg = "datasets/experiment_ssd/2018_07_25_14-00/exported_model/frozen_inference_graph.pb"
        self.labelsArg = "datasets/records/classes.pbtxt"
        self.num_classesArg = 37
        self.min_confidenceArg = 0.5
        filepath = "autoPartsMapping/partNumbers.xlsx"
        self.numberPlateObj = DetectVehicleNumberPlate()


def decodeImageIntoBase64(imgstring, fileName):
    imgdata = base64.b64decode(imgstring)
    with open(fileName, 'wb') as f:
        f.write(imgdata)
        f.close()


def encodeImageIntoBase64(croppedImagePath):
    with open(croppedImagePath, "rb") as f:
        return base64.b64encode(f.read())



@application.route("/predict", methods=["POST"])
def getPrediction():
    
    if request.method == 'POST':
        
        try:
            
            if 'imagefile' not in request.files:
                return render_template("invalid.html")
            
            file = request.files['imagefile']
            
            file.save("Prediction_InputFileFromUser\inputImage.jpg")
            
        except Exception as e:
            return e  

    
    try:
        labelledImage = clApp.numberPlateObj.predictImages(imagePath, pred_stagesArgVal,
                                                           croppedImagepath, clApp.numberPlateObj)
        if labelledImage is not None:
            encodedCroppedImageStr = encodeImageIntoBase64(croppedImagepath)
            ig = str(encodedCroppedImageStr)
            ik = ig.replace('b\'', '')
            numberPlateVal = detect_license_plate(ik)
            if len(numberPlateVal) == 10:
                
                responseDict = {"Number Plate Value: ": numberPlateVal}
            
                #jsonStr = json.dumps(responseDict, ensure_ascii=False).encode('utf8')
                
                #result = Response(jsonStr.decode())
                
                return render_template("result.html",result = responseDict)                                    #Response(jsonStr.decode())
            
            else:
                
                responseDict = {"base64Image": "Unknown", "numberPlateVal": "Unknown"}
                
                jsonStr = json.dumps(responseDict, ensure_ascii=False).encode('utf8')
                
                return Response(jsonStr.decode())
        else:
            
            responseDict = {"base64Image": "Unknown", "numberPlateVal": "Unknown"}
            
            jsonStr = json.dumps(responseDict, ensure_ascii=False).encode('utf8')
            
            return Response(jsonStr.decode())
        
    except Exception as e:
        return render_template("invalid.html")
    
    responseDict = {"base64Image": "Unknown", "numberPlateVal": "Unknown"}
    
    jsonStr = json.dumps(responseDict, ensure_ascii=False).encode('utf8')
    
    return Response(jsonStr.decode())
    



if __name__ == '__main__':
    clApp = ClientApp()
    host = '0.0.0.0'
    port = 5000
    httpd = simple_server.make_server(host, port, application)
    print("Serving on %s %d" % (host, port))
    httpd.serve_forever()
    
    
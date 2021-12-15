from wsgiref import simple_server
from flask import Flask, request, Response
from flask_cors import CORS
import json
from getNumberPlateVals import detect_license_plate
import base64
import os
from predict_images import DetectVehicleNumberPlate

import numpy
import PIL

#Easyocr
import easyocr
reader = easyocr.Reader(['ch_sim','en'])


application = Flask(__name__)

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')
CORS(application)

inputFileName = "inputImage.jpg"
imagePath = "images/" + inputFileName
image_display = True
pred_stagesArgVal = 2
croppedImagepath = "images/croppedImage.jpg"


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
    inpImage = request.json['image']
    decodeImageIntoBase64(inpImage, imagePath)
    
    try:
        labelledImage = clApp.numberPlateObj.predictImages(imagePath, pred_stagesArgVal,
                                                           croppedImagepath, clApp.numberPlateObj)
        if labelledImage is not None:
            labelledImage_RGB = labelledImage.convert("RGB")
            labelledImage_RGB.save("LabelledImage.jpg")
            img = PIL.Image.open("LabelledImage.jpg").convert("L")
            img_array = numpy.array(img)
            
            num_plate = reader.readtext(img_array, detail = 0)
            
            number = num_plate[0]
        
            return number
            
        else:
            
            return None
               
        
    except Exception as e:
        print(e)
    
    responseDict = {"numberPlateVal": "Unknown"}
    
    jsonStr = json.dumps(responseDict, ensure_ascii=False).encode('utf8')
    return Response(jsonStr.decode())
    



if __name__ == '__main__':
    clApp = ClientApp()
    host = '0.0.0.0'
    port = 5000
    httpd = simple_server.make_server(host, port, application)
    print("Serving on %s %d" % (host, port))
    httpd.serve_forever()
    
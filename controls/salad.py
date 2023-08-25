from flask_restful import Resource, request
from flask import make_response, render_template, redirect, send_file, session, Response, jsonify, request, Flask
from models.diseases import tbdiseases, tbsaladtype
from schemas.diseaseschema import diseaseschema, saladtypeschema
from base64 import b64encode
import base64, os
from dbinfo import app
from json import dumps
from werkzeug.utils import secure_filename
from images.diseaseImage import *
from images.saladImage import *
from PIL import Image
from io import BytesIO

from importlib.metadata import files
import tensorflow as tf
import cv2 
import numpy as np
import warnings
import glob
import random
import matplotlib.pyplot as plt

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from tensorflow.lite.python.interpreter import Interpreter

warnings.filterwarnings('ignore') 

class HomePage(Resource):
    @classmethod
    def get(cls):
        return {"msg" : "hello world"}


warnings.filterwarnings('ignore') 

def tflite_detect_images(modelpath, imgpath, lblpath, min_conf=0.5, num_test_images=10, savepath='/save', txt_only=False):

      # Grab filenames of all images in test folder
    images = glob.glob(imgpath + '/*.jpg') + glob.glob(imgpath + '/*.JPG') + glob.glob(imgpath + '/*.png') + glob.glob(imgpath + '/*.bmp')
    # print(imgpath)
    # Load the label map into memory
    
    with open(lblpath, 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    # print('Print : ', labels)
    # Load the Tensorflow Lite model into memory
    interpreter = Interpreter(model_path=modelpath)
    interpreter.allocate_tensors()

    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    float_input = (input_details[0]['dtype'] == np.float32)

    input_mean = 127.5
    input_std = 127.5

    # Randomly select test images
    # IMAGE_PATH = os.path.join(os.pathsep['IMAGE_PATH'])
    images_to_test = [imgpath]  # random.sample(images, num_test_images)

    # Loop over every image and perform detection
    for image_path in images_to_test:

        # Load image and resize to expected shape [1xHxWx3]
        image = cv2.imread(image_path)
        # print('Image : ' , image)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imH, imW, _ = image.shape
        image_resized = cv2.resize(image_rgb, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if float_input:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]['index'],input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[1]['index'])[0] # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[3]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(output_details[0]['index'])[0] # Confidence of detected objects
        
        detections = []

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if ((scores[i] > min_conf) and (scores[i] <= 1.0)):

                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))

                cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                # Draw label
                category_index = label_map_util.create_category_index_from_labelmap(lblpath, use_display_name=True)
                # print('Category : ', category_index)    

                object_name = category_index[int(classes[i])+1] # Look up object name from "labels" array using class index
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(image, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(image, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

                detections.append([object_name, scores[i], xmin, ymin, xmax, ymax])
                print(object_name['id'])
                
    return detections



class ImageUpload(Resource):
    @classmethod
    def post(cls):
        ENCODING = 'utf-8'
        data = request.get_json()
        base64_image = data.get('image', '')
        if base64_image:
            # try:
                image_bytes = base64.b64decode(base64_image)
                image = Image.open(BytesIO(image_bytes))

                image_filename = os.path.join("/Volumes/Seakwin-Drive/Flask+SQL/saladapi/uploadimage/", 'uploaded_image.jpg')
                image.save(image_filename)
                image = cv2.imread(image_filename)
                print(image_filename)


                PATH_TO_IMAGES= image_filename   #'workspace\images\test'   # Path to test images folder
                PATH_TO_MODEL='model.tflite'   # Path to .tflite model file
                PATH_TO_LABELS='label_map.pbtxt' # Path to labelmap.txt file
                min_conf_threshold=0.5   # Confidence threshold (try changing this to 0.01 if you don't see any detection results)
                images_to_test = 10   # Number of images to run detection on
                txt_only = False
                detections = tflite_detect_images(PATH_TO_MODEL, PATH_TO_IMAGES, PATH_TO_LABELS, min_conf_threshold, images_to_test,txt_only)
                image = cv2.imread(PATH_TO_IMAGES)
                if not detections:
                    print('Empty')
                    os.remove(image_filename)
                    return jsonify({'objresponse' : [{'message': 'imageNotFound', 'image_path': '', 'diseaseid' : 0}]})
                else :
                    for detection in detections:
                        class_info, confidence, xmin, ymin, xmax, ymax = detection[0], detection[1], detection[2], detection[3], detection[4], detection[5]
                        
                        # Draw bounding box
                        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
                        
                        # Draw label
                        label = f"{class_info['name']} {int(confidence * 100)}%"
                        cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                        # Save the annotated image to a directory
                        annotated_image_filename = "uploaded_image.jpg"  # Adjust the filename and extension as needed
                        path_to_save = "./uploadimage/" + annotated_image_filename

                        cv2.imwrite(path_to_save, image)

                        getid = detection[0]['id']
                        print(detection)

                    with open(path_to_save, 'rb') as open_file:
                            
                        byte_content = open_file.read()

                    base64_bytes = b64encode(byte_content)
                    base64_string = base64_bytes.decode(ENCODING)

                
               
                # os.remove(image_filename)
                
                return jsonify({'objresponse' : [{'message': 'Image received and processed', 'image_path': base64_string, 'diseaseid' : getid}]})
            # except Exception as e:
                return jsonify({'objresponse' : [{'message': 'Error processing image: ' + str(e)}]}), 400

        return jsonify({'objresponse' : [{'message': 'Image not received', 'image_path': '', 'diseaseid' : 0}]}),
        
class Disease(Resource):
    @classmethod
    def get(cls, did=None):
        try:
            data = tbdiseases.find_by_did(did)
            schema = diseaseschema(many=False)
            _data = schema.dump(data)
            return {"disease": [_data]}
        except Exception as err:
            return {"msg": err}


class DiseaseList(Resource):
    @classmethod
    def get(cls):
        try:
            data = tbdiseases.query.all()
            schema = diseaseschema(many=True)
            _data = schema.dump(data)
            return {"disease": _data}
        except Exception as err:
            return {"msg": err}
        
class SaladType(Resource):
    @classmethod
    def get(cls, sid=None):
        try:
            data = tbsaladtype.find_by_sid(sid)
            schema = saladtypeschema(many=False)
            _data = schema.dump(data)
            return {"saladtype": [_data]}
        except Exception as err:
            return {"msg": err}

class SaladList(Resource):
    @classmethod
    def get(cls):
        try:
            data = tbsaladtype.query.all()
            schema = saladtypeschema(many=True)
            _data = schema.dump(data)
            return {"saladtype": _data}
        except Exception as err:
            return {"msg": err}
        
        
        
def updateDict(listimg=None, typeimglist=None):
    ENCODING = 'utf-8'
    for eachDisease in listimg['images'] :
            with open(eachDisease, 'rb') as open_file:
                byte_content = open_file.read()
            base64_bytes = b64encode(byte_content)

            base64_string = base64_bytes.decode(ENCODING)
            typeimglist.append(base64_string)
        
    return typeimglist

class DiseaseImg(Resource):
    
    @classmethod
    def get(cls,typeimg=None):
        try:
            listOfSalad = [listofSaladIceberg, listofSaladRomaine, listOfSaladLeaf, listOfSaladEndive,listOfSaladArgula]
            listOfDisease = [listOfBaterial, fungalDowny, fungalPowdery, fungalSeptoria, fungalWilt, listOfViral]
            typeimglist = []
            listToEncode = []
            listOfNew = []
            if(typeimg == 'salad'):
                listToEncode = listOfSalad
            elif(typeimg == 'disease'):
                listToEncode = listOfDisease
            for eachDisease in listToEncode:
                updateDict(eachDisease, typeimglist)
                json_data = {'name' : eachDisease["name"], 'images' : typeimglist }
                listOfNew.append(json_data)
                typeimglist = []

            # raw_data = {'image': base64_string}
            # json_data = dumps(raw_data, indent=2)
            if(typeimg == 'salad'):
                return{"saladtypeimg" : listOfNew}
            elif(typeimg == 'disease'):
                return{"diseasetypeimg" : listOfNew}
        except Exception as err:
            return {"msg": err}
class SaladKindImg(Resource):
    
    @classmethod
    def get(cls,typeimg=None):
        try:
            listOfSalad = [listofSaladIceberg, listofSaladRomaine, listOfSaladLeaf, listOfSaladEndive,listOfSaladArgula]
            
            for eachDisease in listOfSalad:
                typeimglist = []
                if(eachDisease["name"] == typeimg):
                    updateDict(eachDisease, typeimglist)
                    json_data = {'name' : eachDisease["name"], 'images' : typeimglist }
                    print(eachDisease["name"])
                    
            return{"saladtypeimg" : [json_data]}
                
        except Exception as err:
            return {"msg": err}
class DiseaseKindImg(Resource):
    
    @classmethod
    def get(cls,typeimg=None):
        try:
            listOfDisease = [listOfBaterial, fungalDowny, fungalPowdery, fungalSeptoria, fungalWilt, listOfViral]
            
            for eachDisease in listOfDisease:
                typeimglist = []
                if(eachDisease["name"] == typeimg):
                    updateDict(eachDisease, typeimglist)
                    json_data = {'name' : eachDisease["name"], 'images' : typeimglist }
                    print(eachDisease["name"])
                    
            return{"diseasetypeimg" : [json_data]}
                
        except Exception as err:
            return {"msg": err}
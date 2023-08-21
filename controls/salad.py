from flask_restful import Resource, request
from flask import make_response, render_template, redirect, send_file, session, Response, jsonify
from models.diseases import tbdiseases, tbsaladtype
from schemas.diseaseschema import diseaseschema, saladtypeschema
from base64 import b64encode
from json import dumps
from images.diseaseImage import *
from images.saladImage import *
class HomePage(Resource):
    @classmethod
    def get(cls):
        return {"msg" : "hello world"}


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
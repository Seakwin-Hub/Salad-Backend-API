from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.diseases import tbdiseases , tbsaladtype
from app import db


class diseaseschema(SQLAlchemyAutoSchema):
    class Meta:
        model = tbdiseases
        sqla_session = db.session
        load_instance = True

    did = auto_field()
    disease = auto_field()
    typeofdisease = auto_field()
    cause = auto_field()
    treatment = auto_field()
    dmeaning = auto_field()
    key = auto_field()

class saladtypeschema(SQLAlchemyAutoSchema):
    class Meta:
        model = tbsaladtype
        sqla_session = db.session
        load_instance = True
    
    sid = auto_field()
    saladname = auto_field()
    descrip = auto_field()
    other = auto_field()


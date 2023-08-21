from app import db

class tbdiseases(db.Model):
    
    did = db.Column("did", db.Integer, primary_key = True)
    disease = db.Column(db.String)
    typeofdisease = db.Column(db.String)
    cause = db.Column(db.String)
    treatment = db.Column(db.String)
    dmeaning = db.Column(db.String)
    key = db.Column(db.String)

    
    def __init__(self, did=None, disease=None, cause=None, treatment=None, dmeaning=None, typeofdisease = None, key = None):
        self.did = did
        self.disease = disease
        self.cause = cause
        self.treatment = treatment
        self.dmeaning = dmeaning
        self.typedisease = typeofdisease
        self.key = key
    
        
    @classmethod
    def find_by_did(cls, did) -> "tbdiseases":
        return cls.query.filter_by(did=did).first()

class tbsaladtype(db.Model):

    sid = db.Column("sid", db.Integer, primary_key=True)
    saladname = db.Column(db.String)
    descrip = db.Column(db.String)
    other = db.Column(db.String)

    def __init__(self, sid=None, saladname=None, descrip=None, other = None):
        self.sid = sid
        self.saladname = saladname
        self.descrip = descrip
        self.other = other



    @classmethod
    def find_by_sid(cls, sid) -> "tbsaladtype":
        return cls.query.filter_by(sid=sid).first()
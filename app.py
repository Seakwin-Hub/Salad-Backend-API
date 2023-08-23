from dbinfo import app, api, db, render_template

import os

from controls.salad import *

@app.errorhandler(404)
def page_not_found(err):
    return {"msg": "page not found"}




api.add_resource(HomePage, "/")
api.add_resource(Disease, "/disease/<did>")
api.add_resource(DiseaseList, "/diseaselist")
api.add_resource(SaladType, "/saladtype/<sid>")
api.add_resource(SaladList, "/saladlist")
api.add_resource(DiseaseImg, "/imagedata/<typeimg>")
api.add_resource(SaladKindImg, "/imagedata/salad/<typeimg>")
api.add_resource(DiseaseKindImg, "/imagedata/disease/<typeimg>")

if __name__ == "__main__":
    db.init_app(app)
    
    app.run(host='0.0.0.0', port=5000, debug=False)

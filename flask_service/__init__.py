#Basic flask + mongodb modified from https://spapas.github.io/2014/06/30/rest-flask-mongodb-heroku/
import os
from flask import Flask
from flask_pymongo import PyMongo
from flask import make_response
from bson.json_util import dumps

MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
	MONGO_URL = "mongodb://localhost:27017/stonkDB"

app = Flask(__name__)
app.config["DEBUG"] = True
app.congig['MONGO_URI'] = MONGO_URL
mongo = PyMongo(app)

def output_json(obj, code, headers=None):
	resp = make_response(dumps(obj), code)
	resp.headers.extend(headers or {})
	return resp
	
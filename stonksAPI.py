#Basic flask + mongodb modified from https://spapas.github.io/2014/06/30/rest-flask-mongodb-heroku/
import os
import time
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask import make_response
from yahooScraper import yahooFinanceScraper as yfs
from bson.json_util import dumps

MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
	MONGO_URL = "mongodb://localhost:27017/stonkDB"

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGO_URI'] = MONGO_URL
mongo = PyMongo(app)

# print(mongo.db.getCollection('currentTickerValues'))

#currentTickerValues

@app.route('/', methods=['GET'])
def home():
	return '''
		<h1>Stonks Viewer API</h1>
		<p>This api fetches the current stock data for a users portfolio</p>
	'''

@app.route('/stonksAPI/v1/current/single', methods=['GET'])
def singleLookup():

	if 'ticker' in request.args:
		ticker = request.args['ticker'].upper()
	else:
		return "Error: No ticker provided. Please specify a ticker."

	cursor = mongo.db.currentTickerValues
	query = {'ticker': ticker}
	stock = cursor.find_one(query, {"_id": 0})
	print('\n',stock,'\n')
	scraper = yfs()
	
	#Fetch new data every 8 hrs
	if stock == None:
		try:
			scraper.runCurrentValueScraper(ticker)
			newData = scraper.getCurrentValueData()[0]
			print('\nNewData:\t',newData)
			cursor.insert_one(newData)
			stock = cursor.find_one(query, {"_id": 0})

		except:
			response = jsonify(stock)
			response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
			return response
	
	elif (time.time() - stock['lastUpdate']) > 28800:
		scraper.runCurrentValueScraper(ticker)
		newData = scraper.getCurrentValueData()[0]
		print('\nNewData Time:\t',newData)
		cursor.update_one(query, {"$set": newData})
		stock = cursor.find_one(query, {"_id": 0})
	
	response = jsonify(stock)
	response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
	return response

app.run()
#Basic flask + mongodb modified from https://spapas.github.io/2014/06/30/rest-flask-mongodb-heroku/
import os
import time
import random
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask import make_response
from yahooScraper import yahooScraper as yfs
from bson.json_util import dumps, loads
from proxyScraper import runScraper as getProxies

siteURL = 'http://localhost:3000'
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

#This method checks the database and updates values as necessary 
@app.route('/stonksAPI/v1/update', methods=['GET'])
def updateValues():
	#First we update the ticker values
	cursor = mongo.db.currentTickerValues
	stocks = cursor.find({}, {'_id': 0})
	scraper = yfs()

	for s in stocks:
		query = {'ticker': s['ticker']}
	
		if (time.time() - s['lastUpdate']) > 28800:
			time.sleep(random.uniform(0,3))
			scraper.runValueScraper(s['ticker'])
			newData = scraper.getCurrentValueData()[0]
			scraper.resetCurrent()

			if newData != []:	
				if newData['price'] != 0.00:
					cursor.update_one(query, {'$set':newData})


	#Second we update the indicies
	cursor2 = mongo.db.indicies
	inds = cursor2.find_one()

	if inds == None:
		x = scraper.runTableScraper('world-indices')
		
		if x:
			newData = scraper.getIndicies()
			cursor2.insert_many(newData)
	else:
		if (time.time() - inds['lastUpdate']) > 28800:
			if scraper.runTableScraper('world-indices'):
				newData = scraper.getIndicies()
				inds = newData
				if newData != []:
					for d in newData:
						cursor2.update_one({'ticker': d['ticker']}, {'$set':d})

	#Third we update the currencies
	cursor3 = mongo.db.currencies
	munny = cursor3.find_one()

	if munny == None:
		if scraper.runTableScraper('currencies'):
			newData = scraper.getCurrencies()
			cursor3.insert_many(newData)
	
	else:
		if (time.time() - munny['lastUpdate']) > 28800:
			if scraper.runTableScraper('currencies'):
				newData = scraper.getCurrencies()
				munny = newData
				if newData != []:
					for d in newData:
						cursor3.update_one({'ticker': d['ticker']}, {'$set':d})	
	response = jsonify({'updated': True})
	response.headers.add('Access-Control-Allow-Origin', siteURL)
	return response

#This function checks if a stock has a valid ticker (if it does and it is new, add it top the database)
@app.route('/stonksAPI/v1/single/exists', methods=['GET', 'POST'])
def checkTickerExists():

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
			scraper.runValueScraper(ticker)
			newData = scraper.getCurrentValueData()[0]
			if newDat['price'] != 0.00:
				cursor.insert_one(newData)
				stock = cursor.find_one(query, {"_id": 0})

		except:
			response = jsonify(stock)
			response.headers.add('Access-Control-Allow-Origin', siteURL)
			return response
	
	elif (time.time() - stock['lastUpdate']) > 28800:
		scraper.runValueScraper(ticker)
		newData = scraper.getCurrentValueData()[0]
		if newData['price'] != 0.00:
			cursor.update_one(query, {"$set": newData})
			stock = cursor.find_one(query, {"_id": 0})
	
	response = jsonify(stock)
	response.headers.add('Access-Control-Allow-Origin', siteURL)
	return response

#Check for the current value of a single stock 
@app.route('/stonksAPI/v1/current/single', methods=['GET', 'POST'])
def singleLookup():
	
	if 'ticker' in request.args:
		ticker = request.args['ticker'].upper()
	else:
		return "Error: No ticker provided. Please specify a ticker."

	cursor = mongo.db.currentTickerValues
	query = {'ticker': ticker}
	stock = cursor.find_one(query, {"_id":0})
	response = jsonify(stock)
	response.headers.add('Access-Control-Allow-Origin', siteURL)
	return response

#Checks for a list of stocks 
@app.route('/stonksAPI/v1/current/multiple', methods=['GET'])
def multipleLookup():

	if 'tickers' in request.args:
		tickers = request.args['tickers'].upper()
	else:
		return 'Error: No tickers provided'
	print(tickers)
	t = tickers.replace('_','.').split(',')
	print(t)
	cursor = mongo.db.currentTickerValues
	query = {'ticker': {"$in":t}}
	stocks = loads(dumps(cursor.find(query, {'_id': 0})))
	response = jsonify(stocks)
	response.headers.add('Access-Control-Allow-Origin', siteURL)
	return response


#This method will look up the current values of indicies
@app.route('/stonksAPI/v1/indicies/current', methods=['GET'])
def indiciesLookup():
	cursor = mongo.db.indicies
	inds = loads(dumps(cursor.find({}, {"_id":0})))
	response = jsonify(inds)
	response.headers.add('Access-Control-Allow-Origin', siteURL)
	return response


#This method will look up the current values of currencies
@app.route('/stonksAPI/v1/currencies/current', methods=['GET'])
def currenciesLookup():
	cursor = mongo.db.currencies
	monies = loads(dumps(cursor.find({}, {"_id": 0})))
	response = jsonify(monies)
	response.headers.add('Access-Control-Allow-Origin', siteURL)
	return response

app.run()
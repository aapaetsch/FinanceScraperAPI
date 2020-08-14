#Basic flask + mongodb modified from https://spapas.github.io/2014/06/30/rest-flask-mongodb-heroku/
import os
import time
import random
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask import make_response
from yahooScraper import yahooScraper as yfs
import yfinance as yf
from bson.json_util import dumps, loads

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
@app.route('/stonksAPI/v1/update', methods=['POST'])
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
    # response = jsonify({'updated': True})
    # response.headers.add('Access-Control-Allow-Origin', siteURL)
    # return response

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
            return sendResponse(stock)
    
    elif (time.time() - stock['lastUpdate']) > 28800:
        scraper.runValueScraper(ticker)
        newData = scraper.getCurrentValueData()[0]
        if newData['price'] != 0.00:
            cursor.update_one(query, {"$set": newData})
            stock = cursor.find_one(query, {"_id": 0})
    
    return sendResponse(stock)

#Check for the current value of a single stock 
@app.route('/stonksAPI/v1/current/single', methods=['GET', 'POST'])
def singleLookup():
    
    if 'ticker' in request.args:
        ticker = request.args['ticker'].upper()
    else:
        return "Error: No ticker provided. Please specify a ticker."

    stock = singleLookup(ticker , mongo.db.currentTickerValues)
    return sendResponse(stock)

#Checks for a list of stocks 
@app.route('/stonksAPI/v1/current/multiple', methods=['GET'])
def multipleLookup():

    if 'tickers' in request.args:
        tickers = request.args['tickers'].upper()
    else:
        return 'Error: No tickers provided'

    t = tickers.replace('_','.')
    stocks = lookupMultiple(t, mongo.db.currentTickerValues)

    return sendResponse(stocks)


#This method will look up the current values of indicies
@app.route('/stonksAPI/v1/indicies/all', methods=['GET'])
def indiciesLookup():
    cursor = mongo.db.indicies
    inds = loads(dumps(cursor.find({}, {"_id":0})))

    return sendResponse(inds)

#This mmethod looks up the current values of a specific index
@app.route('/stonksAPI/v1/indicies/single', methods=['GET'])
def getIndex():

    if 'index' in requests.args:
        index = requests.args['index'].upper()
    else:
        return 'Error: No Index provided'

    try:
        ind = lookupSingle(index, mongo.db.indicies)
        return sendResponse(ind)

    except:
        return sendResponse(None)

    
#This method looks up and returns the values for multiple specific indicies
@app.route('/stonksAPI/v1/indicies/multiple', methods=["GET"])
def getMultipleIndex():

    if 'indicies' in requests.args:
        indicies = requests.args['indicies']
    else:
        return 'Error: Indicies not provided'

    try:
        inds = lookupMultiple(indicies, mongo.db.indicies)
        return sendResponse(inds)

    except:
        return sendResponse(None)




#This method will look up the current values of currencies
@app.route('/stonksAPI/v1/currencies/all', methods=['GET'])
def currenciesLookup():
    cursor = mongo.db.currencies
    monies = loads(dumps(cursor.find({}, {"_id": 0})))
    
    return sendResponse(monies)

#This method looks up the current values of a specific currency
@app.route('/stonksAPI/v1/currencies/single', methods=['GET'])
def getCurrency():
    
    if 'currency' in requests.args:
        currency = requests.args['currency']
    else:
        return 'Error: Currency not provided'

    try:
        curr = lookupSingle(currency, mongo.db.currencies)
        return sendResponse(curr)

    except:
        return sendResponse(None)

#This method looks up the current values for multiple specific currencies
@app.route('/stonksAPI/v1/currencies/multiple', methods=['GET'])
def getMultipleCurrencies():
    
    if 'currencies' in requests.args:
        currencies = requests.args['currencies']
    else:
        return 'Error: Currencies not provided'

    try:
        currs = lookupMultiple(currencies, mongo.db.currencies)
        return sendResponse(currs)

    except:
        return sendResponse(None)


#This method takes in a ticker and a pointer to a mongodb collection, returns the current data for a ticker
def lookupSingle(ticker, cursor):
    query = {'ticker': ticker}
    data = loads(dumps(cursor.find(query, {"_id": 0})))
    return data

#This method takes in multiple tickers as a string and a pointer to a mongodb collection, 
#splits the tickers and returns the current data for each ticker
def lookupMultiple(tickers, cursor):
    ts = tickers.split(',')
    query = {'ticker': {"$in": ts}}
    data = loads(dumps(cursor.find(query, {'_id': 0})))
    return data


#This method takes in some data and formats a response(Incomplete, currently just sets access header and sends json value)
def sendResponse(content):
    response = jsonify(content)
    response.headers.add('Access-Control-Allow-Origin', siteURL)
    return response


app.run()
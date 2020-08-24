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
github = 'https://aapaetsch.github.io'
allowedOrigins = [siteURL, github]
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017/stonkDB"

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGO_URI'] = MONGO_URL
mongo = PyMongo(app)


@app.route('/', methods=['GET'])
def home():
    return '''
        <h1>Stonks Viewer API</h1>
        <p>This api fetches the current stock data for a users portfolio</p>
    '''

#This function updates the data for the requested tickers
#Will take some time, might not want to await response
@app.route('/stonksAPI/v1/update/myTickers', methods=['POST'])
def updateMyTickers():
    if 'tickers' in request.args:
        tickers = request.args['tickers'].upper()
        origin = request.headers['origin']
    
        if checkOrigin(origin) == False:
            return 'Error: Origin not allowed'

    else:
        return 'Error: no tickers present'

    tickersList = tickers.replace('_','.').split(',')
    for ticker in tickersList:
        stock = updateTickerValues(ticker, False)
        updateHistoricalData(ticker)


    return sendResponse({'updated': True}, origin)


#This function updates a ticker's historical data in the db and returns True if it does so successfully
def updateHistoricalData(ticker):

    cursor = mongo.db.historical
    scraper = yfs()

    ticker = ticker.upper()
    data = cursor.find_one({'ticker': ticker}, {'_id':0})
    if data == None:

        try:
            scraper.scrapeHistoricalData(ticker)
            data = scraper.getHistoricalData()
            historicalEntry = {'ticker': ticker, 'lastUpdate': time.time(), 'data': data}
            cursor.insert_one(historicalEntry)
        
            return True

        except: 
            return False


    elif (time.time() - data['lastUpdate']) > 28800:

        try:
            scraper.scrapeHistoricalData(ticker)
            data = scraper.getHistoricalData()
            historicalEntry = {'ticker': ticker, 'lastUpdate': time.time(), 'data': data}
            cursor.update_one({'ticker': ticker}, {'$set':newData})

            return True

        except:
            return False


    return False


#This method checks the database and updates values as necessary 
#Will take some time to execute, we should not wait for a reply from this endpoint
@app.route('/stonksAPI/v1/update/world', methods=['POST'])
def updateValues():
    #First we update the ticker values
    cursor = mongo.db.currentTickerValues
    stocks = cursor.find({}, {'_id': 0})
    scraper = yfs()

    #Second we update the indicies
    cursor2 = mongo.db.indicies
    inds = cursor2.find_one()

    if inds == None:
        x = scraper.runTableScraper('world-indices')
        
        if x:
            newData = scraper.getIndicies()
            #get the currency 
            cursor2.insert_many(newData)
    else:

        if (time.time() - inds['lastUpdate']) > 3600:
        
            if scraper.runTableScraper('world-indices'):
                newData = scraper.getIndicies()
                inds = newData
        
                if newData != []:
        
                    for d in newData:
                        #query db for each indicie, if it doesnt have currency, add it in... 
                        indicie = cursor2.find_one({'ticker': d['ticker']}, {'_id':0})

                        if indicie.get('currency') == None:
                          scraper.resetCurrent()
                          scraper.runValueScraper(d['ticker'])
                          d['currency'] = scraper.getCurrentValueData()[0]['currency']

                        cursor2.update_one({'ticker': d['ticker']}, {'$set':d})

    #Third we update the currencies
    cursor3 = mongo.db.currencies
    munny = cursor3.find_one()

    if munny == None:
        
        if scraper.runTableScraper('currencies'):
            newData = scraper.getCurrencies()
            cursor3.insert_many(newData)
    
    else:
        if (time.time() - munny['lastUpdate']) > 3600:
            
            if scraper.runTableScraper('currencies'):
                newData = scraper.getCurrencies()
                munny = newData
        
                if newData != []:

                    for d in newData:
                        cursor3.update_one({'ticker': d['ticker']}, {'$set':d}) 
   
    return sendResponse({'updated': True}, request.headers['origin'])

#This function checks if a stock has a valid ticker (if it does and it is new, add it top the database)
@app.route('/stonksAPI/v1/single/exists', methods=['GET', 'POST'])
def checkTickerExists():

    if 'ticker' in request.args:
        ticker = request.args['ticker'].upper()
        origin = request.headers['origin']
        
        if checkOrigin(origin) == False:
            return 'Error: Origin not allowed'
    else:
        return "Error: No ticker provided. Please specify a ticker."

    stock = updateTickerValues(ticker, True)
    #need better solution for updating historical data, this will cause lag when a user adds a new stock
    updateHistoricalData(ticker, True)

    return sendResponse(stock, origin)

#This function takes in a ticker, checks if it exists in the database
#Adds it to db if new, updates values if its out of date 
def updateTickerValues(ticker, rush):

    cursor = mongo.db.currentTickerValues
    query = {'ticker': ticker}
    stock = cursor.find_one(query, {"_id": 0})
    print('\n',stock,'\n')
    scraper = yfs()
    
    #Fetch new data every 8 hrs
    if stock == None:
        try:
            scraper.runValueScraper(ticker, rush)
            newData = scraper.getCurrentValueData()[0]
       
            if newDat['price'] != 0.00:
                cursor.insert_one(newData)
                stock = cursor.find_one(query, {"_id": 0})

        except:
            return stock
    
    elif (time.time() - stock['lastUpdate']) > 36000:
        scraper.runValueScraper(ticker, rush)
        newData = scraper.getCurrentValueData()[0]
       
        if newData['price'] != 0.00:
            cursor.update_one(query, {"$set": newData})
            stock = cursor.find_one(query, {"_id": 0})
    
    return stock

#Check for the current value of a single stock 
@app.route('/stonksAPI/v1/current/single', methods=['GET', 'POST'])
def singleLookup():
    
    if 'ticker' in request.args:
        ticker = request.args['ticker'].upper()
        origin = request.headers['origin']
        
        if checkOrigin(origin) == False:
            return 'Error: Origin not allowed'
    else:
        return "Error: No ticker provided. Please specify a ticker."

    stock = singleLookup(ticker , mongo.db.currentTickerValues)
    return sendResponse(stock, origin)

#Checks for a list of stocks 
@app.route('/stonksAPI/v1/current/multiple', methods=['GET'])
def multipleLookup():

    if 'tickers' in request.args:
        tickers = request.args['tickers'].upper()
        origin = request.headers['origin']
        
        if checkOrigin(origin) == False:
            return 'Error: Origin not allowed'
    else:
        return 'Error: No tickers provided'

    t = tickers.replace('_','.')
    stocks = lookupMultiple(t, mongo.db.currentTickerValues)

    return sendResponse(stocks, origin)


#This method will look up the current values of indicies
@app.route('/stonksAPI/v1/indicies/all', methods=['GET'])
def indiciesLookup():
    cursor = mongo.db.indicies
    origin = request.headers['origin']
    inds = loads(dumps(cursor.find({}, {"_id":0})))
    
    if checkOrigin(origin) == False:
        return 'Error: Origin not allowed'

    return sendResponse(inds, origin)

#This method looks up the current values of a specific index
@app.route('/stonksAPI/v1/indicies/single', methods=['GET'])
def getIndex():

    if 'index' in request.args:
        index = request.args['index'].upper()
        origin = request.headers['origin']
        
        if checkOrigin(origin) == False:
            return 'Error: Origin not allowed'
    
    else:
        return 'Error: No Index provided'

    try:
        ind = lookupSingle(index, mongo.db.indicies)
        return sendResponse(ind, origin)

    except:
        return sendResponse(None, origin)

    
#This method looks up and returns the values for multiple specific indicies
@app.route('/stonksAPI/v1/indicies/multiple', methods=["GET"])
def getMultipleIndex():

    if 'indicies' in request.args:
        indicies = request.args['indicies']
        origin = request.headers['origin']
       
        if checkOrigin(origin) == False:
            return 'Error: Origin not allowed'
    
    else:
        return 'Error: Indicies not provided'

    try:
        inds = lookupMultiple(indicies, mongo.db.indicies)
        return sendResponse(inds, origin)

    except:
        return sendResponse(None, origin)




#This method will look up the current values of currencies
@app.route('/stonksAPI/v1/currencies/all', methods=['GET'])
def currenciesLookup():
    cursor = mongo.db.currencies
    origin = request.headers['origin']
    monies = loads(dumps(cursor.find({}, {"_id": 0})))

    if 'form' in request.args:
        returnFormat = request.args['form']
        
        if returnFormat == 'object':
            #We must return it as an object, keys are ticker
            moniesObj = {}
            
            for i in range(len(monies)):
                moniesObj[monies[i]['name']] = monies[i]
            monies = moniesObj

        elif returnFormat != 'array':
            #Since monies is already an array, if the form argument is not object or array, 
            #We will return a None Type
            monies = None

    return sendResponse(monies, origin)

#This method looks up the current values of a specific currency
@app.route('/stonksAPI/v1/currencies/single', methods=['GET'])
def getCurrency():
    
    if 'currency' in request.args:
        currency = request.args['currency']
        origin = request.headers['origin']
       
        if checkOrigin(origin) == False:
            return 'Error: Origin not allowed'
   
    else:
        return 'Error: Currency not provided'

    try:
        curr = lookupSingle(currency, mongo.db.currencies)
        return sendResponse(curr, origin)

    except:
        return sendResponse(None, origin)

#This method looks up the current values for multiple specific currencies
@app.route('/stonksAPI/v1/currencies/multiple', methods=['GET'])
def getMultipleCurrencies():
    
    if 'currencies' in request.args:
        currencies = request.args['currencies']
        origin = request.headers['origin']
        
        if checkOrigin(origin) == False:
            return 'Error: Origin not allowed'
    
    else:
        return 'Error: Currencies not provided'

    try:
        currs = lookupMultiple(currencies, mongo.db.currencies)
        return sendResponse(currs, origin)

    except:
        return sendResponse(None, origin)

@app.route('/stonksAPI/v1/historical/single', methods=['GET'])
def getHistoricalData():

    if 'ticker' in request.args:
        ticker = request.args['ticker']
        origin = request.headers['origin']

        if checkOrigin(origin) == False:
            return 'Error: Origin not allowed'

    else:
        return 'Error: Currencies not provided'

    try:
        start = None
        end = None

        if 'period1' in request.args:
            start = int(request.args['period1'])/1000

        if 'period2' in request.args:
            end = int(request.args['period2'])/1000

        cursor = mongo.db.historical
        #Ignore periods for now, just get the whole 5 years
        query = {'ticker': ticker}
        data = cursor.find_one(query, {'_id': 0})

        return sendResponse(data['data'], origin)

    except: 
        return sendResponse(None, origin)






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
def sendResponse(content, origin):
    response = jsonify(content)
    response.headers.add('Access-Control-Allow-Origin', origin)
    return response

def checkOrigin(origin):
    try: 
        origin = origin.strip('/').lower()
        if origin in allowedOrigins:
            return True
            
    except:
        print('Error: origin not allowed', origin)
        return False




if __name__ == '__main__':
    app.run()
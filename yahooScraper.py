from bs4 import BeautifulSoup as bs
import requests_html
import lxml.html as lh
import time
from datetime import timezone, datetime
import random
import requests


#This class scrapes historical data from yahoo, currenty the period of this data is set to 5 years. 
class yahooHistoryScraper:
    def __init__(self, header):
        self.__historicalData = []
        self.__header = header

    def scrapeHistoricalData(self, ticker, rush):

        #Force a pause between requests, be nice to yahoo...
        if not rush:
            time.sleep(random.uniform(1, 10))

        #1.577E+11 is 5 years in ms
        ticker = ticker.upper()
        end = round(time.time())
        start = round(end - 1.577E+8)
        
        #Throw exception if the url is invalid or returns no data
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history'.format(ticker, start, end)
            r = requests.get(url, allow_redirects=True)
            #Data is returned as bytes-like, turn to string, strip byte-like indicators and split on each line
            dataList = str(r.content).strip('b').strip("'").split('\\n')

            for i in range(len(dataList)):
                #Each line gets split into columns
                dataList[i] = dataList[i].split(',')

            #The first index in dataList is the column names
            columns = dataList.pop(0)

            #Add the data for each day as a dictionary
            for day in dataList:
                data = {}

                for name in range(len(columns)):
                   
                    if name == 0:
                        date = day[name].split('-')
                        t = datetime(int(date[0]), int(date[1]), int(date[2])).replace(tzinfo=timezone.utc).timestamp()
                        data[columns[name]] = t
                   
                    else:
                        data[ columns[ name ] ] = day[ name ]
                
                self.__historicalData.append(data)

        except:
            #Set historical data to none if there is an error in the request
            self.__historicalData = None

    #This method returns the historical data
    def getHistoricalData(self):
        return self.__historicalData

    #This method resets the historical data in cases where we dont want to create an entire new instance of the class
    def resetHistoricalData(self):
        self.__historicalData = []


#This class scrapes the current data for a ticker from yahoo finance
class yahooCurrentValueScraper:
    def __init__(self, header):
        self.__currentValueData = []
        self.__header = header

    def runValueScraper(self, ticker, rush=False):
        #This method scrapes the current quote data for a ticker
        print('\nvalue scraper running {}\n'.format(ticker))
        #Force a pause between requests, be nice to yahoo...
        if not rush:
            time.sleep(random.uniform(1,6))

        ticker = ticker.upper()
        url = 'https://ca.finance.yahoo.com/quote/{}?p={}'.format(ticker, ticker)
        session = requests_html.HTMLSession()
        r = session.get(url, headers=self.__header)
        content = bs(r.content, 'lxml')

        #Try to get the content using its closest ID's 
        try:
            ids = [9, 33, 32]
            data = content.find_all('span', {'data-reactid': ids})

        #Set data to empty if there is an error finding the correct markers
        except:
            data = []

        #If we have an error in any of the data, set all points to 0 or unknown
        if data != []:

            location = data[1]
            price = data[2]
            change = data[3]
            
            #Strip each data point to the raw data that we need 
            location, currency = self.__stripLocation(location)
            price = self.__stripPrice(price)
            change, changePercent = self.__stripChange(change)


        else:
            price = change = changePercent = 0.00
            location = currency = 'Unknown'

        #Strip the stock title
        try:
            stockTitle = content.find_all('h1')
            title = self.__stripTitle(stockTitle[0])

        except:
            title = 'Unknown'

        self.__currentValueData.append({'ticker': ticker, 'price': price, 'currency': currency, 'exchange': location,
        'change': change, 'changePercent': changePercent, 'title': title, 'lastUpdate': time.time()})
    
    #This method allows the user to request multiple tickers at once
    def scrapeMultipleTickers(self, tickers):

        #Run the current value scraper for each ticker
        for ticker in tickers:
            self.runCurrentValueScraper(ticker)
            #Be extra nice to yahoo if we're scraping lots of data at once 
            time.sleep(random.uniform(1,4))

    #This method strips the location for the given content
    def __stripLocation(self, locStr):

        try:
            locList = self.__getCleanList(locStr)
            locList = locList[1].split(' ')
            location = locList[0]
            currency = locList[-1]

        except:
            location = 'Unknown'
            currency = 'Unknown'

        return location, currency

    #This method strips the price for the given content
    def __stripPrice(self, priceStr):

        try: 
            priceList = self.__getCleanList(priceStr)
            price = float(priceList[-1].replace(' ', '').replace(',', ''))
            
        except:
            price = 0.00

        return price

    #This method strips the daily change for the given content
    def __stripChange(self, changeStr):

        #We must get both the change and the percent change, if not set the change to 0
        try:
            changeList = self.__getCleanList(changeStr)
            changeList = changeList[-1].split(' ')
            change = float(changeList[0].replace(' ', '').replace(',', ''))
            changePercent = float(changeList[-1].replace(' ', '').strip('()%').replace(',',''))

        except:
            change = 0.00
            changePercent = 0.00

        return change, changePercent

    #This method strips and returns the title for the given content
    def __stripTitle(self, titleStr):
        try:
            titleList = str(titleStr).strip('</h1>').split('>')
            title = titleList[-1]

        except:
            title = 'Unknown'

        return title

    def __getCleanList(self, string):
        return str(string).strip('</span>').split('>')

    def getCurrentValueData(self):
        return self.__currentValueData

    def resetCurrent(self):
        self.__currentValueData = []


#This class scrapes data from pages with tables on yahoo finance
class yahooTableScraper:
    def __init__(self, header):
        self.__indiciesData = []
        self.__currencies = []
        self.__header = header

    def runTableScraper(self, page):
        #This method can be used to scrape currencies or indicies
        if page != 'currencies' and page != 'world-indices':
            return False
        print('\nscraper running {}\n'.format(page))
        time.sleep(random.uniform(0,6))
        url = 'https://ca.finance.yahoo.com/'+ page
        session = requests_html.HTMLSession()
        r = session.get(url, headers=self.__header)
        content = bs(r.content, 'lxml')
        
        try:
            data = content.find_all('tr')

        except:
            return False


        for d in data:
            content = bs(str(d), 'lxml')
            items = content.find_all('td')
            ind = {}
            colNames = ['ticker', 'name', 'value', 'change', 'changePercent', 'volume']
            i = 0 
            for col in items:
                value = col.contents[0].string

                if value != None:
                    ind[colNames[i]] = value
                i += 1
            
            if ind.get('ticker') != None:
                ind['lastUpdate'] = time.time()
                if page == 'world-indices':
                    self.__indiciesData.append(ind)
                elif page == 'currencies':
                    self.__currencies.append(ind)

        return True

    def getIndicies(self):
        return self.__indiciesData

    def getCurrencies(self):
        return self.__currencies

    def resetCurrencies(self):
        self.__currencies = []

    def resetIndicies(self):
        self.__indiciesData = []

# This class is a wrapper for each scraper class. 
class yahooScraper:
    def __init__(self):
        #Header so we appear as a real browser 
        #TODO: Implement a changing header/variable header
        self.__header = {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
        #Initialize each scraper 
        self.__tableScraper = yahooTableScraper(self.__header)
        self.__currentScraper = yahooCurrentValueScraper(self.__header)
        self.__historicalScraper = yahooHistoryScraper(self.__header)

    # Methods for the current value scraper
    def runValueScraper(self, ticker, rush=False):
        self.__currentScraper.runValueScraper(ticker, rush)

    def scrapeMultipleTickers(self, tickers):
        self.__currentScraper.scrapeMultipleTickers(tickers)

    def getCurrentValueData(self):
        return self.__currentScraper.getCurrentValueData()

    def resetCurrent(self):
        self.__currentScraper.resetCurrent()

    # Methods for the table scraper
    def runTableScraper(self, page):
        return self.__tableScraper.runTableScraper(page)

    def getCurrencies(self):
        return self.__tableScraper.getCurrencies()

    def getIndicies(self):
        return self.__tableScraper.getIndicies()

    def resetIndicies(self):
        self.__tableScraper.resetIndicies()

    def resetCurrencies(self):
        self.__tableScraper.resetCurrencies()

    # Methods for the historical data scraper
    def scrapeHistoricalData(self, ticker, rush=False):
        self.__historicalScraper.scrapeHistoricalData(ticker, rush)

    def getHistoricalData(self):
        return self.__historicalScraper.getHistoricalData()

    def resetHistoricalData(self):
        self.__historicalScraper.resetHistoricalData()





    
    




if __name__ == '__main__':
    scrapy = yahooIndicesScraper()
    scrapy.runScraper()

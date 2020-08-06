from bs4 import BeautifulSoup as bs
import requests_html
import lxml.html as lh
import pandas as pd
from datetime import datetime
from datetime import timedelta
import time
import random
# from collections import OrderedDict
# from itertools import cycle


# proxies = []
# with open('proxies.txt', 'r') as f:
#     for line in f:
#         proxies.append(line)
# print(proxies)
# headers_list = [
#     # Firefox 77 Mac
#      {
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Referer": "https://www.google.com/",
#         "DNT": "1",
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1"
#     },
#     # Firefox 77 Windows
#     {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Referer": "https://www.google.com/",
#         "DNT": "1",
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1"
#     },
#     # Chrome 83 Mac
#     {
#         "Connection": "keep-alive",
#         "DNT": "1",
#         "Upgrade-Insecure-Requests": "1",
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "Sec-Fetch-Site": "none",
#         "Sec-Fetch-Mode": "navigate",
#         "Sec-Fetch-Dest": "document",
#         "Referer": "https://www.google.com/",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
#     },
#     # Chrome 83 Windows 
#     {
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "Sec-Fetch-Site": "same-origin",
#         "Sec-Fetch-Mode": "navigate",
#         "Sec-Fetch-User": "?1",
#         "Sec-Fetch-Dest": "document",
#         "Referer": "https://www.google.com/",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Accept-Language": "en-US,en;q=0.9"
#     },
#     {
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Referer": "https://www.tutorialspoint.com/flask/flask_http_methods.htm",
#         "DNT": "1",
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1"
#     },
#     # Firefox 77 Windows
#     {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Referer": "https://www.google.com/search?q=1+day+in+seconds&rlz=1C1CHBF_enCA867CA867&oq=1+day+in+seconds&aqs=chrome..69i57j6.2720j0j4&sourceid=chrome&ie=UTF-8",
#         "DNT": "1",
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1"
#     },
#     # Chrome 83 Mac
#     {
#         "Connection": "keep-alive",
#         "DNT": "1",
#         "Upgrade-Insecure-Requests": "1",
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "Sec-Fetch-Site": "none",
#         "Sec-Fetch-Mode": "navigate",
#         "Sec-Fetch-Dest": "document",
#         "Referer": "https://blog.upperlinecode.com/flask-and-firebase-and-pyrebase-oh-my-f30548d68ea9",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
#     },
#     # Chrome 83 Windows 
#     {
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "Sec-Fetch-Site": "same-origin",
#         "Sec-Fetch-Mode": "navigate",
#         "Sec-Fetch-User": "?1",
#         "Sec-Fetch-Dest": "document",
#         "Referer": "https://www.google.com/",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Accept-Language": "en-US,en;q=0.9"
#     }
#     ,
#     # Chrome 83 Windows 
#     {
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "Sec-Fetch-Site": "same-origin",
#         "Sec-Fetch-Mode": "navigate",
#         "Sec-Fetch-User": "?1",
#         "Sec-Fetch-Dest": "document",
#         "Referer": "https://www.google.com/",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Accept-Language": "en-US,en;q=0.9"
#     }
# ]

# ordered_headers_list = []
# for headers in headers_list:
#     h = OrderedDict()
#     for header, value in headers.items():
#         h[header]=value
#     ordered_headers_list.append(h)
# random.shuffle(proxies)
# proxy_pool = cycle(proxies)


class yahooScraper:
    def __init__(self):
        self.__currentValueData = []
        self.__indiciesData = []
        self.header = {
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

    def runValueScraper(self, ticker):
        #This method scrapes the current quote data for a ticker
        print('\n\n\n\n\nscraper running\n\n\n\n\n\n\n')
        time.sleep(random.uniform(0,6))
        # p = next(proxy_pool).replace('\n','')
        ticker = ticker.upper()
        url = 'https://ca.finance.yahoo.com/quote/{}?p={}'.format(ticker, ticker)
        session = requests_html.HTMLSession()
        r = session.get(url, headers=self.header)
        content = bs(r.content, 'lxml')
        
        # try:
        #     # r = session.get(url,proxies={'https': p, 'http': p}, headers=random.choice(headers_list))

        # except:
        #     self.runScraper(ticker)
        #     print('Error with proxie:', p)
        #     proxies.remove(p)

        try:
            ids = [9, 33, 32]
            # random.shuffle(ids)
            # make the scraper more robust
            data = content.find_all('span', {'data-reactid': ids})

        except:
            data = []

        if data != []:

            location = data[1]
            price = data[2]
            change = data[3]
            
            location, currency = self.__stripLocation(location)
            price = self.__stripPrice(price)
            change, changePercent = self.__stripChange(change)
        else:
            price = change = changePercent = 0.00
            location = currency = 'Unknown'

        try:
            stockTitle = content.find_all('h1')
            title = self.__stripTitle(stockTitle[0])
        except:
            #redundant....
            title = 'Unknown'


        self.__currentValueData.append({'ticker': ticker, 'price': price, 'currency': currency, 'exchange': location,
        'change': change, 'changePercent': changePercent, 'title': title, 'lastUpdate': time.time()})
    
    def scrapeMultipleTickers(self, tickers):
        for ticker in tickers:
            self.runCurrentValueScraper(ticker)
            time.sleep(random.uniform(0,4))

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

    def __stripPrice(self, priceStr):
        try: 
            priceList = self.__getCleanList(priceStr)
            price = float(priceList[-1].replace(' ', '').replace(',', ''))
            
        except:
            price = 0.00

        return price

    def __stripChange(self, changeStr):
        try:
            changeList = self.__getCleanList(changeStr)
            changeList = changeList[-1].split(' ')
            change = float(changeList[0].replace(' ', '').replace(',', ''))
            changePercent = float(changeList[-1].replace(' ', '').strip('()%').replace(',',''))
        except:
            change = 0.00
            changePercent = 0.00

        return change, changePercent

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

    def runTableScraper(self, page):
        #This method can be used to scrape currencies or indicies
        if page != 'currencies' or page != 'indicies':
            return False
        print('\n\n\n\n\nscraper running\n\n\n\n\n\n\n')
        time.sleep(random.uniform(0,6))
        url = 'https://ca.finance.yahoo.com/'+ page
        session = requests_html.HTMLSession()
        r = session.get(url, headers=self.header)
        content = bs(r.content, 'lxml')
        
        try:
            print(content)
            data = content.find_all('tr')
            print(data)
        except:
            return False


        for d in data:
            content = bs(d, 'lxml')
            items = content.find_all('td')
            ind = {}
            colNames = ['ticker', 'name', 'value', 'change', 'changePercent', 'volume']
            i = 0 
            for col in items:
                value = col.contents[0].string
                if value != None:
                    print(value)
                    ind[colNames[i]] = value
                i += 1
            
            if ind.get('ticker') != None:
                ind['lastUpdate'] = time.time()
                if page == 'indicies':
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

    def resetCurrent(self):
        self.__currentValueData = []




if __name__ == '__main__':
    scrapy = yahooIndicesScraper()
    scrapy.runScraper()

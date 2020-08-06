from bs4 import BeautifulSoup as bs
import requests_html
import lxml.html as lh
import pandas as pd
from datetime import datetime
from datetime import timedelta
import time
import random

class yahooFinanceScraper:
	def __init__(self):
		self.__currentValueData = []
	
	def runCurrentValueScraper(self, ticker):
		print('\n\n\n\n\nscraper running\n\n\n\n\n\n\n')
		ticker = ticker.upper()
		url = 'https://ca.finance.yahoo.com/quote/{}?p={}'.format(ticker, ticker)
		session = requests_html.HTMLSession()
		r = session.get(url)
		content = bs(r.content, 'lxml')

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
			time.sleep(random.uniform(2))

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



if __name__ == '__main__':
	scrapy = yahooFinanceScraper('vgg.to')
	scrapy.runScraper()
	print(scrapy.getAll())

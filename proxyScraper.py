from bs4 import BeautifulSoup as bs
import requests_html
import lxml.html as lh


def runScraper():
	url = "https://free-proxy-list.net"
	session = requests_html.HTMLSession()
	r = session.get(url)
	content = bs(r.content, 'lxml')

	try:
		data = content.find_all('td')
		noArguments = []
		for d in data: 
			item = str(d)
			if '<td>' in item:
				if '.' in item:
					noArguments.append(item.replace('<td>', '').replace('</td>', ''))
	except:
		print('error')
		return []

	return noArguments




if __name__ == '__main__':
	runScraper()
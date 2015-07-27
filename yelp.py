from threading import Thread
from uuid import uuid4
import urllib
import json
import time
import re
from bs4 import BeautifulSoup
import requests
import sys
from operator import itemgetter
import unicodecsv
import os
import urlparse
from commonregex import CommonRegex


def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

def in_parallel(fn, l):
       for i in l:
           Thread(target=fn, args=(i,)).start()
		   
 
def extract_data(htmllink):
		
		html = load_page(htmllink)

		category = html.find(attrs={'class': re.compile(r".*\bcategory-str-list\b.*")})
		if(category):
				category = re.sub(' +',' ',category.text.strip())
		else:
				category = ''

		title = html.find(attrs={'class': re.compile(r".*\bbiz-page-title\b.*")})
		if(title):
				title = re.sub(' +',' ',title.text.strip())
		else:
				title = ''
		if html.find(attrs={'class': re.compile(r".*\baddress\b.*")}):
			address = html.find(attrs={'class': re.compile(r".*\baddress\b.*")}).text.strip()
			address = re.sub(' +',' ',address)
		else:
			address = ''

		if html.find(attrs={'class': re.compile(r".*\bbiz-phone\b.*")}):
			phone = html.find(attrs={'class': re.compile(r".*\bbiz-phone\b.*")}).text.strip()
			phone = re.sub(' +',' ',phone)
		else:
			phone = ''

		if html.find(attrs={'class': re.compile(r".*\bbiz-website\b.*")}):
			website = html.find(attrs={'class': re.compile(r".*\bbiz-website\b.*")}).text.strip()
			website = re.sub(' +',' ',website.replace("Business website",""))
		else:
			website = ''

		# if website:
		# 	html = load_page(website)
		# 	email = getmails(html.get_text())
		# 	email = ' ,'.join(email)

		
		print category, title, address
		if website:
			with open('pictureframe.csv', 'a+') as csvfile:
					wrObj = unicodecsv.writer(csvfile, delimiter=',',quotechar='"', quoting=unicodecsv.QUOTE_MINIMAL)
					wrObj.writerow([iriToUri(htmllink),category, title, address,phone,website])
 
def get_ads_links(p):
		linkul = p.find(attrs={'class': re.compile(r".*\bsearch-results\b.*")})
		# linkli = linkul.find('ul')
		adslink = []
		if linkul:
			for ad in linkul.find_all('li'):
				tmp = ad.find('h3')
				if tmp:
					tmp = tmp.find('a')
					if 'adredir' not in tmp['href']:
						print 'http://www.yelp.com'+tmp['href']
						adslink.append('http://www.yelp.com'+tmp['href'])

		return adslink
def getmails(text):
	reobj = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,6}\b", re.IGNORECASE)
	return re.findall(reobj, text.decode('utf-8'))


def load_page(u):
		if 'http://' not in u:
			u = 'http://'+u
		proxies = {
			"http": "52.26.100.39:21320"
		}
		
		r             = requests.get(u,proxies=proxies)
		data            = r.text
		soup          = BeautifulSoup(data)
		return soup
 
def from_page(u):
		proxies = {
			"http": "52.26.100.39:21320"
		}
		r             = requests.get(u,proxies=proxies)
		r             = r.text
		print r
		r 			  = json.loads(r)

		data             = r['search_results']
		soup          = BeautifulSoup(data)
		return soup
		
 
def generatePaginationLinks():
	for x in xrange(0,99):
		resultRange= x*10;
		link = 'http://www.yelp.com/search/snippet?find_desc=picture+frame+store&find_loc=WA&start='+str(x*10)+'&parent_request_id=f43c140dd157cbef&request_origin=user'
		print "\n", link
		ads = get_ads_links(from_page(link))
		in_parallel(extract_data,ads)
		time.sleep(2)
		# sys.exit()


generatePaginationLinks()
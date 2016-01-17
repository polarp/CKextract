# -*- coding: utf-8 -*-

import requests
import json
from lxml import html
from urlparse import urljoin, urlsplit
from datetime import date, timedelta, datetime

def get(url, retry=None):
	if retry is None:
		retry = 6

	try:
		q = requests.get(url)
	except:
		if retry > 0:
			retry = retry - 1
			return get(url, retry)

		return None

	return q

def date_range(start=None, end=None):
    span = end - start
    for i in xrange(span.days + 1):
        yield start + timedelta(days=i)

def process_page(data, date_, url):
	title_selector = '//span/h1[@class="mk"]/text()'
	more_selector = '//span[@class="tekst_opis"]/a/@href'
	image_selector = '//div[@class="indexopis"]/img/@src'
	fasting_foods_selector = '//td[@onclick="document.location.href=\'{}\'"]/span/text()'.format(urlsplit(url).path)

	doc = html.fromstring(data)

	titles = doc.xpath(title_selector)
	description_links = doc.xpath(more_selector)

	holidays = list()
	for t, d in zip(titles, description_links):
		holidays.append({'name': t.encode('utf-8'),
						 'color': 'црн',
						 'descriptionUrl': urljoin(url, d)})

	return dict({'dayOfYear': str(date_.timetuple().tm_yday),
				'nationalHoliday': None,
				'imageUrl': '',
				'holidays': holidays,
				'fastingFoods': [i.encode('utf-8') for i in doc.xpath(fasting_foods_selector)]})

def main():
	format_ = '%Y-%m-%d'
	base_url = 'http://crkvenikalendar.com/datummk-{}-{}-{}'
	
	start = datetime.strptime('2016-01-01', format_).date()
	end = datetime.strptime('2016-12-31', format_).date()

	data = list()
	for dt in date_range(start, end):
		url = base_url.format(dt.year, dt.month, dt.day)

		q = get(url)
		if q is None:
			continue

		data.append(process_page(q.content, dt, url))

	with open('data.json', 'w') as out:
	     json.dump(data, out, sort_keys = True, indent = 4, ensure_ascii=False)

if __name__=='__main__':
	main()
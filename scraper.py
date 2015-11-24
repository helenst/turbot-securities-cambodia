# -*- coding: utf-8 -*-

import json
import datetime
import re
import requests
import string
import turbotlib
from bs4 import BeautifulSoup


def normalize_whitespace(text):
    return " ".join(map(strip_whitespace, text.split()))


def strip_whitespace(text):
    return text.strip(string.whitespace + u'\u200b')


class Page(object):
    def __init__(self, url):
        self._url = url
        self._current_category = ''
        self._page_title = ''

    def capture(self, filename):
        """
        capture contents of the page to html file
        """
        html = requests.get(self._url).content
        open(filename, 'w').write(html)

    def process(self):
        if FETCH_REAL_DATA:
            turbotlib.log("Scraping {}...".format(self._url))
            html = requests.get(self._url).content
        else:
            html = open('settlement.html').read()

        doc = BeautifulSoup(html)
        self._page_title = normalize_whitespace(doc.find('h2').text)
        rows = doc.find(class_='market_participant').table.find_all('tr')

        return self.process_rows(rows)

    def process_rows(self, rows):
        for number, row in enumerate(rows, 1):
            if row.find(class_='h_title'):
                pass
            elif row.find(class_='h_title2'):
                self._current_category = normalize_whitespace(row.text)
            else:
                yield self.process_entry(row, number)

    def process_entry(self, row, number):
        cells = row.find_all('td')[-2:]
        name_cell, contact_cell = cells
        name = normalize_whitespace(name_cell.text)
        info = {
            'number': number,
            'name': name,
            'type': self._page_title,
            'category': self._current_category,
            'sample_date': datetime.datetime.now().isoformat(),
            'source_url': self._url,
        }
        info.update(self.process_contact_info(contact_cell))
        return info

    def process_contact_info(self, cell):
        lines = map(
            strip_whitespace,
            re.split('[\r\n]+', cell.text, re.UNICODE)
        )
        lines = filter(None, lines)
        info = {
            'address': normalize_whitespace(lines[0]),
        }
        for line in lines[1:]:
            parts = map(strip_whitespace, line.split(':'))
            if len(parts) == 2:
                if parts[0]:
                    key = parts[0].lower()
                value = parts[1]
            else:
                value = strip_whitespace(line)

            info.setdefault(key, [])
            info[key].append(value)
        return info

FETCH_REAL_DATA = True

ids = ['m52', 'm51', 'm511', 'm512']

urls = [
    'http://www.secc.gov.kh/english/{}.php?pn=6'.format(id_)
    for id_ in ids
]

for url in urls:
    for row in Page(url).process():
        print json.dumps(row)

#page = Page(SOURCE_URL)
#page.capture('settlement.html')

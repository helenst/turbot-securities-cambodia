# -*- coding: utf-8 -*-

import json
import datetime
import requests
import turbotlib
from bs4 import BeautifulSoup

SOURCE_URL = 'http://www.secc.gov.kh/english/m52.php?pn=6'
FETCH_REAL_DATA = False


def normalize(text):
    return " ".join(token.strip() for token in text.split())


class Page(object):
    def __init__(self, url):
        self._url = url
        self._current_category = None

    def capture(self):
        """
        capture contents of the page to html file
        """
        html = requests.get(self._url).content
        open('source.html', 'w').write(html)

    def process(self):
        if FETCH_REAL_DATA:
            turbotlib.log("Scraping {}...".format(self._url))
            html = requests.get(self._url).content
        else:
            html = open('source.html').read()

        doc = BeautifulSoup(html)
        rows = doc.find(class_='market_participant').table.find_all('tr')

        return self.process_rows(rows)

    def process_rows(self, rows):
        for number, row in enumerate(rows, 1):
            if row.find(class_='h_title'):
                pass
            elif row.find(class_='h_title2'):
                self._current_category = normalize(row.text)
            else:
                yield self.process_entry(row, number)

    def process_entry(self, row, number):
        name_cell, contact_cell = row.find_all('td')
        name = normalize(name_cell.text)
        info = {
            'number': number,
            'name': name,
            'category': self._current_category,
            'sample_date': datetime.datetime.now().isoformat(),
            'source_url': self._url,
        }
        info.update(self.process_contact_info(contact_cell))
        return info

    def process_contact_info(self, cell):
        lines = filter(None, cell.text.split('\r\n'))
        info = {
            'address': normalize(lines[0]),
        }
        for line in lines[1:]:
            parts = [item.strip() for item in line.split(':')]
            if len(parts) == 2:
                if parts[0]:
                    key = parts[0].lower()
                value = parts[1]
            else:
                value = line.strip()

            info.setdefault(key, [])
            info[key].append(value)
        return info


for row in Page(SOURCE_URL).process():
    print json.dumps(row)

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
    return text.strip(string.whitespace + u'\u200b\u00a0')


def normalize_key(key):
    if key == 'web':
        return 'website'
    elif key == 'e-mail':
        return 'email'
    else:
        return key


class Page(object):
    def __init__(self, page_id):
        self._page_id = page_id
        self._page_title = ''
        self._current_category = ''

    @property
    def url(self):
        return 'http://www.secc.gov.kh/english/{}.php?pn=6'.format(self._page_id)

    @property
    def filename(self):
        return 'data/{}.php?pn=6'.format(self._page_id)

    def process(self):
        if FETCH_REAL_DATA:
            turbotlib.log("Scraping {}...".format(self.url))
            html = requests.get(self.url).content
        else:
            html = open(self.filename).read()

        doc = BeautifulSoup(html)
        self._page_title = normalize_whitespace(doc.find('h2').text)
        rows = doc.find(class_='market_participant').table.find_all('tr')

        return self.process_rows(rows)

    def process_rows(self, rows):
        for row in rows:
            if row.find(class_='h_title'):
                pass
            elif row.find(class_='h_title2'):
                self._current_category = normalize_whitespace(row.text)
            else:
                yield self.process_entry(row)

    def process_entry(self, row):
        # Only look at the last two cells
        # (There might be a first cell with a logo)
        name_cell, contact_cell = row.find_all('td')[-2:]
        name = normalize_whitespace(name_cell.text)
        info = {
            'name': name,
            'type': self._page_title,
            'category': self._current_category,
            'sample_date': datetime.datetime.now().isoformat(),
            'source_url': self.url,
        }
        info.update(self.process_contact_info(contact_cell))
        return info

    def process_contact_info(self, cell):
        lines = map(
            strip_whitespace,
            re.split('[\r\n]+', cell.text, re.UNICODE)
        )
        lines = filter(None, lines)

        # First line is always address
        info = {
            'address': normalize_whitespace(lines[0]),
        }
        for line in lines[1:]:
            parts = map(strip_whitespace, line.split(':'))
            if len(parts) == 2:
                if parts[0]:
                    key = normalize_key(parts[0].lower())
                value = parts[1]
            else:
                value = strip_whitespace(line)

            info.setdefault(key, [])
            info[key].append(value)
        return info

FETCH_REAL_DATA = False

ids = ['m52', 'm51', 'm511', 'm512']

for page_id in ids:
    for row in Page(page_id).process():
        print json.dumps(row)

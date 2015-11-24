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


def process_entry(row, category):
    name_cell, contact_cell = row.find_all('td')
    name = normalize(name_cell.text)
    lines = filter(None, contact_cell.text.split('\r\n'))
    info = {
        'name': name,
        'category': category,
        'address': normalize(lines[0]),
        'sample_date': datetime.datetime.now().isoformat(),
        'source_url': SOURCE_URL,
    }
    for line in lines[1:]:
        parts = [item.strip() for item in line.split(':')]
        if len(parts) == 2:
            # save the last key
            if parts[0]:
                key = parts[0].lower()
            value = parts[1]
        else:
            value = line.strip()

        info.setdefault(key, [])
        info[key].append(value)
    return info


def process_rows(rows):
    category = None
    for row in rows:
        if row.find(class_='h_title'):
            pass
        elif row.find(class_='h_title2'):
            category = normalize(row.text)
        else:
            print json.dumps(process_entry(row, category))


if FETCH_REAL_DATA:
    turbotlib.log("Scraping {}...".format(SOURCE_URL))
    html = requests.get(SOURCE_URL).content
else:
    html = open('source.html').read()

doc = BeautifulSoup(html)
rows = doc.find(class_='market_participant').table.find_all('tr')
process_rows(rows)

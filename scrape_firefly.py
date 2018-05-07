#!/usr/bin/python

import requests
import re
import json
import datetime
from dateutil.relativedelta import relativedelta

DASHING_URL = 'http://localhost:3030/widgets/bills'
DASHING_API_KEY = ''

FIREFLY_BASE = 'http://127.0.0.1:8090/%s'
FIREFLY_LOGIN = FIREFLY_BASE % 'login'
FIREFLY_BILLS = FIREFLY_BASE % 'json/box/bills'
FIREFLY_DATECHANGE = FIREFLY_BASE % 'daterange'
FIREFLY_USERNAME = ''
FIREFLY_PASSWORD = ''


now = datetime.datetime.now()
date_from = datetime.datetime(year=now.year, month=now.month, day=15)
date_to = datetime.datetime(year=now.year, month=now.month, day=14)
if now.day < 15:
    date_from = (date_from - relativedelta(months=1))
else:
    date_to = (date_to + relativedelta(months=1))

# Create session for requests to firefly
s = requests.session()

# Get login page and grab token
login_get = s.get(FIREFLY_LOGIN)
auth_token_re = re.search(r'name="_token" value="([a-zA-Z0-9]+)"', login_get.text)

# Perform login
s.post(FIREFLY_LOGIN, data={'_token': auth_token_re.group(1), 'email': FIREFLY_USERNAME, 'password': FIREFLY_PASSWORD})

r = s.get(FIREFLY_BASE % '')
token = re.search(r'<meta name="csrf-token" content="([a-zA-Z0-9]+)">', r.text)

# Update date range
r = s.post(FIREFLY_DATECHANGE, data={'_token': token.group(1), 'label': 'Custom+range', 'start': date_from.strftime('%Y-%m-%d'), 'end': date_to.strftime('%Y-%m-%d')})
print r.text
# Obtain bills
bills = s.get(FIREFLY_BILLS).json()
unpaid = round(float(bills['unpaid'][1:].replace(',', '')), 2)
paid = round(float(bills['paid'][1:].replace(',', '')), 2)
total = unpaid + paid
perc_unpaid = round(((paid / total) * 100))

# Update dashboard
r = requests.post(DASHING_URL, data=json.dumps({'auth_token': DASHING_API_KEY, 'title': 'Bills Paid<br />&pound;%s Left' % unpaid, 'value': perc_unpaid}))
print r.text

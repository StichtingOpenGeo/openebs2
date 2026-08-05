#!/usr/bin/env python3
"""Log in to a running server and check the main pages come back.

Usage: smoke.py http://127.0.0.1:8000
"""
import http.cookiejar
import os
import re
import sys
import urllib.parse
import urllib.request

BASE = sys.argv[1].rstrip('/')
USERNAME = os.environ.get('SMOKE_USER', 'smoke')
PASSWORD = os.environ.get('SMOKE_PASSWORD', 'smoke-password')

PAGES = [
    ('/bericht', None),
    ('/bericht/nieuw', None),
    ('/kaart', 'autocomplete_holder'),  # The stop search box, see #234
    ('/haltes.geojson', 'FeatureCollection'),
    ('/stop/search.json?q=Den+Haag', 'Den Haag'),
    ('/scenario', None),
    ('/ritaanpassing', None),
    ('/admin/', None),
]

opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
failures = []


def fetch(path, data=None):
    url = BASE + path
    request = urllib.request.Request(url, data=data, headers={'Referer': url})
    with opener.open(request) as response:
        return response.getcode(), response.read().decode('utf-8', 'replace')


def check(path, contains=None):
    try:
        status, body = fetch(path)
    except Exception as error:  # urllib raises on 4xx/5xx
        failures.append('%s -> %s' % (path, error))
        print('FAIL %s (%s)' % (path, error))
        return
    if status != 200:
        failures.append('%s -> %s' % (path, status))
    elif contains and contains not in body:
        failures.append('%s -> 200 but missing %r' % (path, contains))
    else:
        print('ok   %s (%s)' % (path, status))
        return
    print('FAIL %s' % failures[-1])


def login():
    _, body = fetch('/inloggen/')
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', body)
    if not match:
        sys.exit('no csrf token on the login page')
    data = urllib.parse.urlencode({
        'csrfmiddlewaretoken': match.group(1),
        'username': USERNAME,
        'password': PASSWORD,
    }).encode()
    _, body = fetch('/inloggen/', data=data)
    if 'Uitloggen' not in body:
        sys.exit('login as %s failed' % USERNAME)
    print('ok   logged in as %s' % USERNAME)


check('/inloggen/')
login()
for page, contains in PAGES:
    check(page, contains)

if failures:
    sys.exit('\n%d check(s) failed:\n  %s' % (len(failures), '\n  '.join(failures)))
print('\nall checks passed')

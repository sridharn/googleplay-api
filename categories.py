#!/usr/bin/python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

try:
    # Python 2
    import urlparse
except ImportError:
    # Python 3
    import urllib.parse as urlparse

from googleplay_api.googleplay import GooglePlayAPI

# read config from config.py
config = GooglePlayAPI.read_config()

# connect to GooglePlayStore
api = GooglePlayAPI(config)
api.login()
response = api.browse()

print("ID", "Name", sep=config['SEPARATOR'])
for c in response.category:
    category = urlparse.parse_qs(c.dataUrl)['cat'][0]
    name = c.name
    print(category, name, sep=config['SEPARATOR'])


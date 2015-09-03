#!/usr/bin/python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from google.protobuf import text_format

try:
    # Python 2
    import urlparse
except ImportError:
    # Python 3
    import urllib.parse as urlparse

import helpers
from googleplay import GooglePlayAPI

# read config from config.py
config = helpers.read_config()

# connect to GooglePlayStore
api = GooglePlayAPI(config['ANDROID_ID'])
api.login(config['GOOGLE_LOGIN'], config['GOOGLE_PASSWORD'], config['AUTH_TOKEN'])
response = api.browse()

print(config['SEPARATOR'].join(["ID", "Name"]))
for c in response.category:
    category = urlparse.parse_qs(c.dataUrl)['cat'][0]
    name = c.name
    print(config['SEPARATOR'].join([category, name]))


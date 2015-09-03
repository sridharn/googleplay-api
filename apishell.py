#!/usr/bin/python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

BANNER = """
Google Play Unofficial API Interactive Shell
Successfully logged in using your Google account. The variable 'api' holds the API object.
Feel free to use help(api).
"""

import sys
import code
from google.protobuf import text_format

import helpers

try:
    # Python 2
    import urlparse
except ImportError:
    # Python 3
    import urllib.parse as urlparse

from googleplay import GooglePlayAPI

# read config from config.py
config = GooglePlayAPI.read_config()

# connect to GooglePlayStore
api = GooglePlayAPI(config['ANDROID_ID'])
api.login(config['GOOGLE_LOGIN'], config['GOOGLE_PASSWORD'], config['AUTH_TOKEN'])
code.interact(BANNER, local=locals())

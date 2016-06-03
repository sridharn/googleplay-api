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

import helpers
from googleplay_api.googleplay import GooglePlayAPI

if (len(sys.argv) < 2):
    print("Usage: %s packagename1 [packagename2 [...]]" % sys.argv[0])
    print("Display permissions required to install the specified app(s).")
    sys.exit(0)

packagenames = sys.argv[1:]

# read config from config.py
config = GooglePlayAPI.read_config()

# connect to GooglePlayStore
api = GooglePlayAPI(config)
api.login()

# Only one app
if (len(packagenames) == 1):
    response = api.details(packagenames[0])
    for item in response.docV2.details.appDetails.permission:
        print(helpers.str_compat(item))

else: # More than one app
    response = api.bulkDetails(packagenames)

    for entry in response.entry:
        if (not not entry.ListFields()): # if the entry is not empty
            print(entry.doc.docid + ":")
            for item in entry.doc.details.appDetails.permission:
                print("    " + helpers.str_compat(item))
            print()


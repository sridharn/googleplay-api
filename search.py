#!/usr/bin/python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

import helpers
from googleplay_api.googleplay import GooglePlayAPI

if (len(sys.argv) < 2):
    print("Usage: %s request [nb_results] [offset]" % sys.argv[0])
    print("Search for an app.")
    print("If request contains a space, don't forget to surround it with \"\"")
    sys.exit(0)

request = sys.argv[1]
nb_res = None
offset = None

if (len(sys.argv) >= 3):
    nb_res = int(sys.argv[2])

if (len(sys.argv) >= 4):
    offset = int(sys.argv[3])

# read config from config.py
config = GooglePlayAPI.read_config()

# connect to GooglePlayStore
api = GooglePlayAPI(config['ANDROID_ID'])
api.login(config['GOOGLE_LOGIN'], config['GOOGLE_PASSWORD'], config['AUTH_TOKEN'])

try:
    message = api.search(request, nb_res, offset)
except:
    print("Error: something went wrong. Maybe the nb_res you specified was too big?")
    sys.exit(1)

helpers.print_header_line()
doc = message.doc[0]
for c in doc.child:
    helpers.print_result_line(c)


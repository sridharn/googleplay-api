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
    print("Usage: %s category [subcategory] [nb_results] [offset]" % sys.argv[0])
    print("List subcategories and apps within them.")
    print("category: To obtain a list of supported catagories, use categories.py")
    print("subcategory: You can get a list of all subcategories available, by supplying a valid category")
    sys.exit(0)

cat = sys.argv[1]
ctr = None
nb_results = None
offset = None

if (len(sys.argv) >= 3):
    ctr = sys.argv[2]
if (len(sys.argv) >= 4):
    nb_results = sys.argv[3]
if (len(sys.argv) == 5):
    offset = sys.argv[4]

# read config from config.py
config = GooglePlayAPI.read_config()

# connect to GooglePlayStore
api = GooglePlayAPI(config['ANDROID_ID'])
api.login(config['GOOGLE_LOGIN'], config['GOOGLE_PASSWORD'], config['AUTH_TOKEN'])

try:
    message = api.list(cat, ctr, nb_results, offset)
except:
    print("Error: HTTP 500 - one of the provided parameters is invalid")
    sys.exit(1)

if (ctr is None):
    print("Subcategory ID", "Name", sep=config['SEPARATOR'])
    for doc in message.doc:
        print(helpers.str_compat(doc.docid), helpers.str_compat(doc.title), sep=config['SEPARATOR'])
else:
    helpers.print_header_line()
    doc = message.doc[0]
    for c in doc.child:
        helpers.print_result_line(c)


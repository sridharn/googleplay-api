# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import logging

config = None

def read_config(config_file='config.py'):
    """
    Read the repository config

    The config is read from config_file, which is in the current directory.
    """
    global config

    if config is not None:
        return config
    if not os.path.isfile(config_file):
        logging.critical("Missing config file.")
        sys.exit(2)

    config = dict()

    logging.debug("Reading %s" % config_file)
    with io.open("config.py", "rb") as f:
        code = compile(f.read(), "config.py", 'exec')
        exec(code, None, config)

    return config


def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

def print_header_line():
    if config == None:
        read_config()

    l = [ "Title",
                "Package name",
                "Creator",
                "Super Dev",
                "Price",
                "Offer Type",
                "Version Code",
                "Size",
                "Rating",
                "Num Downloads",
             ]
    print(*l, sep=config['SEPARATOR'])

def print_result_line(c):
    if config == None:
        read_config()

    #c.offer[0].micros/1000000.0
    #c.offer[0].currencyCode
    l = [ c.title,
                c.docid,
                c.creator,
                len(c.annotations.badgeForCreator), # Is Super Developer?
                c.offer[0].formattedAmount,
                c.offer[0].offerType,
                c.details.appDetails.versionCode,
                sizeof_fmt(c.details.appDetails.installationSize),
                "%.2f" % c.aggregateRating.starRating,
                c.details.appDetails.numDownloads]
    print(*l, sep=config['SEPARATOR'])


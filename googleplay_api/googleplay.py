#!/usr/bin/python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import logging
import requests
import sys

from google.protobuf import descriptor
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from google.protobuf import text_format
from google.protobuf.message import Message

from googleplay_api import googleplay_pb2

logging.basicConfig(format="%(message)s")
logger = logging.getLogger(__name__)


class LoginError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RequestError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

config = None


class GooglePlayAPI(object):
    """Google Play Unofficial API Class

    Usual APIs methods are login(), search(), details(), bulkDetails(),
    download(), browse(), reviews() and list().

    toStr() can be used to pretty print the result (protobuf object) of the
    previous methods.

    toDict() converts the result into a dict, for easier introspection."""

    SERVICE = "androidmarket"
    URL_LOGIN = "https://android.clients.google.com/auth" # "https://www.google.com/accounts/ClientLogin"
    ACCOUNT_TYPE_GOOGLE = "GOOGLE"
    ACCOUNT_TYPE_HOSTED = "HOSTED"
    ACCOUNT_TYPE_HOSTED_OR_GOOGLE = "HOSTED_OR_GOOGLE"

    def __init__(self, config, debug=False):
        self.preFetch = {}
        self.androidId = config.get('ANDROID_ID')
        self.lang = config.get('LANG')
        self.email = config.get('GOOGLE_LOGIN')
        self.password = config.get('GOOGLE_PASSWORD')
        self.auth_token = None
        self.sdk_version = config.get('SDK_VERSION')
        self.proxy = config.get('PROXY')

        if debug:
            logger.setLevel(logging.DEBUG)

    @staticmethod
    def read_config(config_file="config.py"):
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
        with io.open(config_file, "rb") as f:
            code = compile(f.read(), "config.py", "exec")
            exec(code, None, config)

        return config

    @classmethod
    def toDict(cls, protoObj):
        """Converts a protobuf object from an API call into a dict for easier introspection."""
        iterable = False
        if isinstance(protoObj, RepeatedCompositeFieldContainer):
            iterable = True
        else:
            protoObj = [protoObj]
        retlist = []

        for po in protoObj:
            msg = dict()
            for fielddesc, value in po.ListFields():
                logger.debug("{} {} {}".format(value, type(value), getattr(value, "__iter__", False)))
                if fielddesc.type == descriptor.FieldDescriptor.TYPE_GROUP or \
                   isinstance(value, RepeatedCompositeFieldContainer) or \
                   isinstance(value, Message):
                    msg[fielddesc.name] = cls.toDict(value)
                else:
                    msg[fielddesc.name] = value
            retlist.append(msg)
        if not iterable:
            if len(retlist) > 0:
                return retlist[0]
            else:
                return None
        return retlist

    @staticmethod
    def toStr(protoObj):
        """Used for pretty printing a result from the API."""
        return text_format.MessageToString(protoObj)

    def _try_register_preFetch(self, protoObj):
        fields = [i.name for (i, _) in protoObj.ListFields()]
        if ("preFetch" in fields):
            for p in protoObj.preFetch:
                self.preFetch[p.url] = p.response

    def set_auth_token(self, auth_token):
        self.auth_token = auth_token
        logging.debug("auth token: %s" % auth_token)

    def login(self):
        """Login to your Google Account."""

        params = {
            "Email": self.email,
            "Passwd": self.password,
            "service": self.SERVICE,
            "accountType": self.ACCOUNT_TYPE_HOSTED_OR_GOOGLE,
            "has_permission": "1",
            "source": "android",
            "androidId": self.androidId,
            "app": "com.android.vending",
            #"client_sig": self.client_sig,
            "device_country": "us",
            "operatorCountry": "us",
            "lang": "us",
            "sdk_version": self.sdk_version
        }
        headers = {
            "Accept-Encoding": "",
        }
        response = requests.post(self.URL_LOGIN, data=params, headers=headers, proxies=self.proxy, verify=True)
        data = response.text.split()
        params = {}
        for d in data:
            if not "=" in d: continue
            k, v = d.split("=", 1)
            params[k.strip().lower()] = v.strip()
        if "auth" in params:
            logger.debug("Auth-Token found: %s" % params["auth"])
            self.set_auth_token(params["auth"])
        elif "error" in params:
            raise LoginError("server says: " + params["error"])
        else:
            raise LoginError("Auth token not found.")

    def executeRequestApi2(self, path, datapost=None, post_content_type="application/x-www-form-urlencoded; charset=UTF-8"):
        if datapost is None and path in self.preFetch:
            data = self.preFetch[path]
        else:
            headers = {
                "Accept-Language": self.lang,
                "Authorization": "GoogleLogin auth=%s" % self.auth_token,
                "X-DFE-Enabled-Experiments": "cl:billing.select_add_instrument_by_default",
                "X-DFE-Unsupported-Experiments": "nocache:billing.use_charging_poller,market_emails,buyer_currency,prod_baseline,checkin.set_asset_paid_app_field,shekel_test,content_ratings,buyer_currency_in_app,nocache:encrypted_apk,recent_changes",
                "X-DFE-Device-Id": self.androidId,
                "X-DFE-Client-Id": "am-android-google",
                "User-Agent": "Android-Finsky/4.4.3 (api=3,versionCode=8016014,sdk=22,device=hammerhead,hardware=hammerhead,product=hammerhead)",
                "X-DFE-SmallestScreenWidthDp": "335",
                "X-DFE-Filter-Level": "3",
                "Accept-Encoding": "",
                "Host": "android.clients.google.com",
            }

            if datapost is not None:
                headers["Content-Type"] = post_content_type

            url = "https://android.clients.google.com/fdfe/%s" % path
            if datapost is not None:
                response = requests.post(url, data=datapost, headers=headers, proxies=self.proxy, verify=True)
            else:
                response = requests.get(url, headers=headers, proxies=self.proxy, verify=True)
            data = response.content
        message = googleplay_pb2.ResponseWrapper.FromString(data)
        self._try_register_preFetch(message)

        logger.debug(text_format.MessageToString(message))
        return message

    #####################################
    # Google Play API Methods
    #####################################

    def search(self, query, nb_results=None, offset=None):
        """Search for apps."""
        path = "search?c=3&q=%s" % requests.utils.quote(query) # TODO handle categories
        if (nb_results is not None):
            path += "&n=%d" % int(nb_results)
        if (offset is not None):
            path += "&o=%d" % int(offset)

        message = self.executeRequestApi2(path)
        return message.payload.searchResponse

    def details(self, packageName):
        """Get app details from a package name.
        packageName is the app unique ID (usually starting with 'com.')."""
        path = "details?doc=%s" % requests.utils.quote(packageName)
        message = self.executeRequestApi2(path)
        return message.payload.detailsResponse

    def bulkDetails(self, packageNames):
        """Get several apps details from a list of package names.

        This is much more efficient than calling N times details() since it
        requires only one request.

        packageNames is a list of app ID (usually starting with 'com.')."""
        path = "bulkDetails"
        req = googleplay_pb2.BulkDetailsRequest()
        req.docid.extend(packageNames)
        data = req.SerializeToString()
        message = self.executeRequestApi2(path, data, "application/x-protobuf")
        return message.payload.bulkDetailsResponse

    def browse(self, cat=None, ctr=None):
        """Browse categories.
        cat (category ID) and ctr (subcategory ID) are used as filters."""
        path = "browse?c=3"
        if (cat != None):
            path += "&cat=%s" % requests.utils.quote(cat)
        if (ctr != None):
            path += "&ctr=%s" % requests.utils.quote(ctr)
        message = self.executeRequestApi2(path)
        return message.payload.browseResponse

    def list(self, cat, ctr=None, nb_results=None, offset=None):
        """List apps.

        If ctr (subcategory ID) is None, returns a list of valid subcategories.

        If ctr is provided, list apps within this subcategory."""
        path = "list?c=3&cat=%s" % requests.utils.quote(cat)
        if (ctr != None):
            path += "&ctr=%s" % requests.utils.quote(ctr)
        if (nb_results != None):
            path += "&n=%s" % requests.utils.quote(nb_results)
        if (offset != None):
            path += "&o=%s" % requests.utils.quote(offset)
        message = self.executeRequestApi2(path)
        return message.payload.listResponse

    def reviews(self, packageName, filterByDevice=False, sort=2, nb_results=None, offset=None):
        """Browse reviews.
        packageName is the app unique ID.
        If filterByDevice is True, return only reviews for your device."""
        path = "rev?doc=%s&sort=%d" % (requests.utils.quote(packageName), sort)
        if (nb_results is not None):
            path += "&n=%d" % int(nb_results)
        if (offset is not None):
            path += "&o=%d" % int(offset)
        if(filterByDevice):
            path += "&dfil=1"
        message = self.executeRequestApi2(path)
        return message.payload.reviewResponse

    def download(self, packageName, versionCode, offerType=1):
        """Download an app and return its raw data (APK file).

        packageName is the app unique ID (usually starting with 'com.').

        versionCode can be grabbed by using the details() method on the given
        app."""
        path = "purchase"
        data = "ot=%d&doc=%s&vc=%d" % (offerType, packageName, versionCode)
        message = self.executeRequestApi2(path, data)

        url = message.payload.buyResponse.purchaseStatusResponse.appDeliveryData.downloadUrl
        logger.debug(message)
        logger.debug(message.payload)
        try:
            cookie = message.payload.buyResponse.purchaseStatusResponse.appDeliveryData.downloadAuthCookie[0]
        except IndexError:
            raise Exception("Did not receive downloadAuthCookie!")

        cookies = {
            str(cookie.name): str(cookie.value) # python-requests #459 fixes this
        }

        headers = {
            "User-Agent": "AndroidDownloadManager/4.1.1 (Linux; U; Android 4.1.1; Nexus S Build/JRO03E)",
            "Accept-Encoding": "",
        }

        response = requests.get(url, headers=headers, cookies=cookies, proxies=self.proxy, verify=True)
        return response.content

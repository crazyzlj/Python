#!/usr/bin/python
from cookielib import CookieJar
from urllib import urlencode

import urllib2

# The user credentials that will be used to authenticate access to the data

username = "zhuliangjun"
password = "Liangjun0130"

# The url of the file we wish to retrieve

url = "http://disc2.gesdisc.eosdis.nasa.gov/data//TRMM_L3/TRMM_3B42_Daily.7/" \
      "2016/10/3B42_Daily.20161019.7.nc4"

# Create a password manager to deal with the 401 reponse that is returned from
# Earthdata Login

password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_manager.add_password(None, "https://urs.earthdata.nasa.gov", username, password)

# Create a cookie jar for storing cookies. This is used to store and return
# the session cookie given to use by the data server (otherwise it will just
# keep sending us back to Earthdata Login to authenticate).  Ideally, we
# should use a file based cookie jar to preserve cookies between runs. This
# will make it much more efficient.

cookie_jar = CookieJar()

# Install all the handlers.

opener = urllib2.build_opener(
    urllib2.HTTPBasicAuthHandler(password_manager),
    # urllib2.HTTPHandler(debuglevel=1),    # Uncomment these two lines to see
    # urllib2.HTTPSHandler(debuglevel=1),   # details of the requests/responses
    urllib2.HTTPCookieProcessor(cookie_jar))
urllib2.install_opener(opener)

# Create and submit the request. There are a wide range of exceptions that
# can be thrown here, including HTTPError and URLError. These should be
# caught and handled.

request = urllib2.Request(url)
response = urllib2.urlopen(request)

# Print out the result (not a good idea with binary data!)

body = response.read()
print body

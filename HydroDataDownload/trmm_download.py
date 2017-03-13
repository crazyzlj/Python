#! /usr/bin/env python
# coding=utf-8
# Author: Liangjun Zhu
# Date  : 2016-4-7
# Email : zlj@lreis.ac.cn
# Blog  : zhulj.net

import urllib2
import os
import sys
import time


def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


def mkdir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)


def downloadByUrl(curUrl, filePath):
    f = urllib2.urlopen(curUrl)
    data = f.read()
    with open(filePath, "wb") as code:
        code.write(data)


def findUrlTxts(path):
    tempFiles = os.listdir(path)
    urlTxts = []
    for s in tempFiles:
        if s.split(".")[-1] == 'txt':
            urlTxts.append(path + os.sep + s)
    return urlTxts


def ReadUrls(files):
    urls = []
    for file in files:
        curF = open(file)
        for line in curF:
            line = line.split('\n')[0]
            urls.append(line)
        curF.close()
    return urls


def findStations(urls):
    stations = []
    for curUrl in urls:
        temp = curUrl.split("?")[0]
        fileName = temp.split("/")[-1]
        sss = fileName.split('-')
        for ss in sss:
            if len(ss) == 5 and not ss in stations:
                stations.append(ss)
    return stations

def climateDown(urls, savePath, usrname = '', pwd = '', eachNum = 200, timeout = 5):
    count = 1
    allcount = len(urls)
    for curUrl in urls:
        saveName = curUrl.split("/")[-1]
        curSavePath = savePath + os.sep + saveName
        if count % eachNum == 0:
            time.sleep(timeout)
        if usrname != '' and pwd != '':
            downNASAEarthdata(curUrl, curSavePath, usrname, pwd)
        else:
            downloadByUrl(curUrl, curSavePath)
        print " %d / %d,  %s" % (count, allcount, saveName)
        count += 1

def downNASAEarthdata(curUrl, curSavePath, usrname, pwd):
    from cookielib import CookieJar
    from urllib import urlencode
    import urllib2

    # The user credentials that will be used to authenticate access to the data
    #
    # username = "zhuliangjun"
    # password = "Liangjun0130"
    #
    # # The url of the file we wish to retrieve
    #
    # url = "http://disc2.gesdisc.eosdis.nasa.gov/data//TRMM_L3/TRMM_3B42_Daily.7/" \
    #       "2016/10/3B42_Daily.20161019.7.nc4"

    # Create a password manager to deal with the 401 reponse that is returned from
    # Earthdata Login

    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, "https://urs.earthdata.nasa.gov", usrname, pwd)

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

    request = urllib2.Request(curUrl)
    response = urllib2.urlopen(request)

    # Print out the result (not a good idea with binary data!)

    data = response.read()
    with open(curSavePath, "wb") as code:
        code.write(data)

if __name__ == '__main__':
    CUR_PATH = currentPath()
    CUR_PATH = r'C:\Users\ZhuLJ\Desktop\TRMM_download'
    usrname = 'zhuliangjun'
    pwd = 'Liangjun0130'
    DOWN_PATH = CUR_PATH + os.sep + 'download'
    mkdir(DOWN_PATH)
    urlTxts = findUrlTxts(CUR_PATH)
    urls = ReadUrls(urlTxts)
    climateDown(urls, DOWN_PATH, usrname = usrname, pwd = pwd)


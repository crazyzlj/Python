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


def isStationNeeded(name):
    temp = name.split('-')
    flag = False
    for s in temp:
        if len(s) == 5:
            flag = True
            break
    return flag


def climateDown(urls, savePath, eachNum = 200, timeout = 5):
    count = 1
    allcount = len(urls)
    for curUrl in urls:
        temp = curUrl.split("?")[0]
        saveName = temp.split("/")[-1]
        if isStationNeeded(saveName):
            curSavePath = savePath + os.sep + saveName
            if count % eachNum == 0:
                time.sleep(timeout)
            downloadByUrl(curUrl, curSavePath)
            print " %d / %d,  %s" % (count, allcount, saveName)
            count += 1


if __name__ == '__main__':
    CUR_PATH = currentPath()
    CUR_PATH = r'C:\Users\ZhuLJ\Desktop\climate_data_download'
    DOWN_PATH = CUR_PATH + os.sep + 'download'
    mkdir(DOWN_PATH)
    urlTxts = findUrlTxts(CUR_PATH)
    urls = ReadUrls(urlTxts)
    climateDown(urls, DOWN_PATH, 200, 5)

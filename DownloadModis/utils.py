#! /usr/bin/env python
# coding=utf-8
# Author: Liangjun Zhu
# Date  : 2017-1-11
# Email : zlj@lreis.ac.cn
# Blog  : zhulj.net

import os
import sys
import time
import datetime
import subprocess


def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


def mkdir(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)


def savedata2file(data, filepath):
    with open(filepath, "ab") as code:
        code.write(data)


def StringMatch(str1, str2):
    if str1.lower() == str2.lower():
        return True
    else:
        return False


def list2datetime(datelist):
    try:
        if len(datelist) == 1:
            return datetime.datetime(datelist[0])
        elif len(datelist) == 2:
            return datetime.datetime(datelist[0], datelist[1])
        elif len(datelist) == 3:
            return datetime.datetime(datelist[0], datelist[1], datelist[2])
        elif len(datelist) == 4:
            return datetime.datetime(datelist[0], datelist[1], datelist[2], datelist[3])
        elif len(datelist) == 5:
            return datetime.datetime(datelist[0], datelist[1], datelist[2], datelist[3], datelist[4])
    except TypeError:
        print ("Invalid inputs for datetime!")


def isfileexist(filepath):
    if os.path.exists(filepath) and os.path.isfile(filepath):
        return True
    else:
        return False


def delfile(filepath):
    if isfileexist(filepath):
        os.remove(filepath)


def IsLeapYear(year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    else:
        return False


def GetDayNumber(year, month):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    elif IsLeapYear(year):
        return 29
    else:
        return 28


def doy(dt):
    sec = time.mktime(dt.timetuple())
    t = time.localtime(sec)
    return t.tm_yday


def print2log(msg, print2screen=True, logfile=None):
    if logfile is not None:
        f = open(logfile, 'a')
        f.write(msg)
        f.close()
    if print2screen:
        print (msg)


def isnumerical(x):
    try:
        xx = float(x)
    except TypeError:
        return False
    except ValueError:
        return False
    except 'Exception':
        return False
    else:
        return True


def runcommand(commands):
    """
    Execute external command, and return the output lines list
    :param commands: string or list
    :return: output lines
    """
    print (commands)
    use_shell = True
    if isinstance(commands, list) or isinstance(commands, tuple):
        use_shell = False
    process = subprocess.Popen(commands, shell = use_shell, stdout = subprocess.PIPE, stdin = open(os.devnull),
                               stderr = subprocess.STDOUT, universal_newlines = True)
    return process.stdout.readlines()


def zipfiles(filenames, zip_file):
    commands = ['python', '-m', 'zipfile', '-c', zip_file]
    if filenames:
        for filename in filenames:
            commands.append(filename)
        runcommand(commands)

def locateStringInList(str, strlist):
    found = False
    foundstr = []
    for tmpstr in strlist:
        if str in tmpstr:
            found = True
            foundstr.append(tmpstr)
    return found, foundstr


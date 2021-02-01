# coding=utf-8
# Author: Liangjun Zhu
# Date  : 2017-3-13
# Email : zlj@lreis.ac.cn
# Blog  : zhulj.net

from utils import *
import urllib2
from bs4 import BeautifulSoup

import ssl
from functools import wraps


def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)

    return bar


ssl.wrap_socket = sslwrap(ssl.wrap_socket)


def chunk_report(mbytes_so_far, total_size):
    if total_size > 0:
        percent = float(mbytes_so_far) / total_size
        percent = round(percent * 100, 2)
        sys.stdout.write("Downloaded %.3f of %.3f Mb (%0.2f%%)\r" %
                         (mbytes_so_far, total_size, percent))
        if mbytes_so_far >= total_size:
            sys.stdout.write('\n')
    else:
        pass  # currently, do nothing


def chunk_read(response, chunk_size=8192, savepath=None, report_hook=None):
    try:
        total_size = response.info().getheader('content-length').strip()
        total_size = float(total_size) / 1024. / 1024.
    except AttributeError:
        total_size = 0.
    bytes_so_far = 0

    while True:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk) / 1024. / 1024.
        if not chunk:
            break
        if savepath is not None:
            savedata2file(chunk, savepath)
        if report_hook:
            report_hook(bytes_so_far, total_size)
    return bytes_so_far


def downMODISfromNASAEarthdata(productname, **kwargs):
    from cookielib import CookieJar
    downUrl = 'https://e4ftl01.cr.usgs.gov/MOLT/'
    prefix = productname.split('.')[0]
    version = productname.split('.')[1]
    usrname = ''
    pwd = ''
    startdate = datetime.datetime.today()
    enddate = datetime.datetime.today()
    h = 0
    v = 8
    deltaday = 8
    outpath = ''
    # try to get the required key-values, or throw exception
    try:
        usrname = kwargs["usrname"]
        pwd = kwargs["pwd"]
        startdate = kwargs["startdate"]
        enddate = kwargs["enddate"]
        h = kwargs["h"]
        v = kwargs["v"]
        deltaday = kwargs["deltaday"]
        outpath = kwargs["workspace"]
    except KeyError:
        print ("downMODISfromNASAEarthdata function must have the usrname, pwd, startdate, and enddate args.")
    # try to get optional key-values
    logfile = None
    if 'log' in kwargs.keys():
        logfile = kwargs['log']
        delfile(logfile)

    authorizeUrl = "https://urs.earthdata.nasa.gov"
    # Create a password manager to deal with the 401 response that is returned from authorizeUrl
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, authorizeUrl, usrname, pwd)
    cookie_jar = CookieJar()
    opener = urllib2.build_opener(
        urllib2.HTTPBasicAuthHandler(password_manager),
        # urllib2.HTTPHandler(debuglevel=1),    # Uncomment these two lines to see
        # urllib2.HTTPSHandler(debuglevel=1),   # details of the requests/responses
        urllib2.HTTPCookieProcessor(cookie_jar))
    urllib2.install_opener(opener)

    tmpdate = startdate
    while tmpdate <= enddate:
        curdownUrl = downUrl + productname + '/' + tmpdate.strftime("%Y.%m.%d") + '/'
        print curdownUrl
        itemsList = read_url(curdownUrl)
        curItem = prefix + '.A%d%03d.h%02dv%02d.' % (tmpdate.year, doy(tmpdate), h, v) + version
        found, curItemUrls = locateStringInList(curItem, itemsList)
        if not found:
            print ("File %s not found!" % curItem)
            continue
        for curItemUrl in curItemUrls:
            tmpfile = outpath + os.sep + os.path.split(curItemUrl)[1]
            delfile(tmpfile)
            try:
                print2log(curItemUrl, logfile = logfile)
                request = urllib2.Request(curItemUrl)
                response = urllib2.urlopen(request)
                chunk_read(response, savepath = tmpfile, report_hook = chunk_report)
            except urllib2.HTTPError or urllib2.URLError, e:
                print e.code
        tmpdate += datetime.timedelta(days = deltaday)


def read_url(url):
    url = url.replace(" ", "%20")
    try:
        req = urllib2.Request(url)
        a = urllib2.urlopen(req).read()
        soup = BeautifulSoup(a, 'html.parser')
        x = (soup.find_all('a'))
        allurl = []
        for i in x:
            file_name = i.extract().get_text()
            url_new = url + file_name
            url_new = url_new.replace(" ", "%20")
            allurl.append(url_new)
        return allurl
    except urllib2.HTTPError or urllib2.URLError, e:
        print e.code


if __name__ == '__main__':
    DOWN_PATH = r'D:\tmp'
    product = "MOD15A2H.006"
    usrname = 'your_user_name'
    pwd = 'your_password'
    startdate = [2002, 2, 18]  # year, month, day
    enddate = [2002, 3, 5]
    deltaday = 8
    h = 1
    v = 11
    log = DOWN_PATH + os.sep + product + '.log'
    downMODISfromNASAEarthdata(product, usrname = usrname, pwd = pwd,
                               startdate = list2datetime(startdate),
                               enddate = list2datetime(enddate),
                               deltaday = deltaday, h = h, v = v,
                               workspace = DOWN_PATH, log = log)

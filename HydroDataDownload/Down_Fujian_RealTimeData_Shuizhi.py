
# coding=utf-8
#
# 福建省地表水水质实时信息公开系统(试运行)
#   https://szfb.fjeec.cn:444/AutoData/Business/DataPublish_FJ/index.html
#
#
#
# Created by Liangjun Zhu (zlj@lreis.ac.cn)
# Updated: 08/17/2020
from __future__ import unicode_literals

import os
import json
import datetime
from io import open
import requests
from requests.exceptions import RequestException

from apscheduler.schedulers.blocking import BlockingScheduler
from pygeoc.utils import UtilClass

REAL_URL = 'https://szfb.fjeec.cn:444/API/PublicService/ShuiZhiFaBu/GetRealData?AreaID=&RiverID='
REQ_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
               'Authorization': 'Public_Web=6A607FAB00686B7B363BD9A81B835649'}


def get_realtime_data():
    try:
        response = requests.get(REAL_URL, headers=REQ_HEADERS)
        if response.status_code == 200:
            tmpstr = response.text
            tmpstr = tmpstr.replace('\r\n', '')
            tmpstr = tmpstr.replace('\n', '')
            tmpstr = tmpstr.replace('\r', '')
            return tmpstr
        return None
    except RequestException:
        print('Get data failed from %s' % REAL_URL)


def down_routinely(savedir):
    """Write response string to log file and Parsed JSON to YYYY-MM-DD-HH.json file."""
    ctime = datetime.datetime.now()
    ctime_str = ctime.strftime('%Y-%m-%d %H:%M:%S')
    print('Executed at %s' % ctime_str)

    dstring = get_realtime_data()
    with open(savedir + os.sep + 'FJ_realdata_shuizhi.data', 'a', encoding='utf-8') as logf:
        if dstring is None:
            logf.write('[%s]  Get data failed!\n' % ctime_str)
        else:
            logf.write('[%s]  %s\n' % (ctime_str, dstring))
    if dstring is None:
        return

    djson = json.loads(dstring)
    if 'ResultList' not in djson:
        return
    if len(djson['ResultList']) < 1:
        return
    if 'DataTime' not in djson['ResultList'][0]:
        return
    data_time_str = djson['ResultList'][0]['DataTime']
    data_time = datetime.datetime.strptime(data_time_str, '%Y/%m/%d %H:%M')

    rawdir = wp + os.sep + 'raw_data'
    UtilClass.mkdir(rawdir)
    json_name = '%s.json' % (data_time.strftime('%Y-%m-%d-%H'))
    json_file = rawdir + os.sep + json_name

    if os.path.exists(json_file):
        with open(savedir + os.sep + 'FJ_realdata_shuizhi.log', 'a', encoding='utf-8') as logf:
            logf.write('[%s]  %s already exist.\n' % (ctime_str, json_name))
    else:
        with open(json_file, 'w', encoding='utf-8') as jf:
            jf.write(json.dumps(djson, indent=4, ensure_ascii=False))
        with open(savedir + os.sep + 'FJ_realdata_shuizhi.log', 'a', encoding='utf-8') as logf:
            logf.write('[%s]  %s saved successfully.\n' % (ctime_str, json_name))


if __name__ == "__main__":
    wp = UtilClass.current_path(lambda: 0)
    # wp = 'D:\\tmp\\fujian_shuizhi_realtime'
    UtilClass.mkdir(wp)

    sched = BlockingScheduler()
    sched.add_job(down_routinely, args=[wp], trigger='interval', seconds=10800)
    sched.start()

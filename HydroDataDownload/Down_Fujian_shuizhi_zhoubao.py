
# coding=utf-8
#
# 从福建省生态环境厅网站下载水质周报数据，该网站采用Ajax技术实现数据查询
#   http://sthjt.fujian.gov.cn/gzcy/bmfwcx/szcx/
#
# Created by Liangjun Zhu (zlj@lreis.ac.cn)
# Updated: 08/14/2020
from __future__ import unicode_literals

import os
import json
from collections import OrderedDict
from io import open

import requests
from requests.exceptions import RequestException
import xlwt
from future.utils import iteritems
from pygeoc.utils import FileClass, UtilClass, StringClass

REQ_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
BASEURL = 'http://sthjt.fujian.gov.cn'
SEARCH_URL = '/was5/web/search?channelid=280067&prepage=15&classsql=dockind=10' \
             '%20*s4%20%3D%20{}%20and%20s5%20%3D%20{}&page={}&r'
# e.g., dockind=10%20*s4%20%3D%202020%20and%20s5%20%3D%201
#       can be parsed as: dockind=10 *s4 = 2020 and s5 = 1

# Selected fields and the corresponding title names
SEL_FIELDS = {'s1': '水系',
              's2': '点位名称',
              's3': '断面情况',
              's4': '年',
              's5': '周',
              # 's6': '起始日期',
              # 's7': '终止日期',
              'f1': 'pH',
              'f2': 'DO(mg/L)',
              'f3': 'CODmn(mg/L)',
              'f4': 'TP(mg/L)',
              'f5': 'NH3-N(mg/L)',
              'f6': '总氮',
              's8': '上周水质',
              's9': '本周水质',
              's10': '主要污染指标'}
TITLES = ['s4', 's5', 's1', 's2', 's3',  # 's6', 's7',
          'f1', 'f2', 'f3', 'f4', 'f5', 'f6',
          's8', 's9', 's10']


def write_data_to_xls(datadict, newfile):
    newdict = OrderedDict()
    if type(datadict) is list or type(datadict) is tuple:
        newdict['Sheet1'] = datadict
    elif type(datadict) is dict or type(datadict) is OrderedDict:
        newdict = datadict
    else:
        return
    newworkbook = xlwt.Workbook()
    for k, v in iteritems(newdict):
        if len(v) < 1:
            continue
        tmpsheet = newworkbook.add_sheet(k)
        for row in list(range(len(v))):
            for col in list(range(len(v[row]))):
                tmpsheet.write(row, col, v[row][col])

    newworkbook.save(newfile)


def get_one_page(url):
    try:
        response = requests.get(url, headers=REQ_HEADERS)
        if response.status_code == 200:
            tmpstr = response.text
            tmpstr = tmpstr.replace('\r\n', '')
            tmpstr = tmpstr.replace('\n', '')
            tmpstr = tmpstr.replace('\r', '')
            return tmpstr
        return None
    except RequestException:
        print('Get data failed from %s' % url)


def down_year_week(yr, wk, page, savedir, next_page=True):
    print('  Page: %d' % page)
    # Do not download repeatedly
    json_file = savedir + os.sep + '%d%02d%02d.json' % (yr, wk, page)
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as jf:
            tmpjson = json.load(jf)
    else:
        tmpurl = BASEURL + SEARCH_URL.format(yr, wk, page)
        tmpstr = get_one_page(tmpurl)
        tmpjson = json.loads(tmpstr)
    # print(tmpjson)
    if 'pagenum' not in tmpjson:
        return
    page_num = StringClass.extract_numeric_values_from_string(tmpjson['pagenum'])
    if page_num is None or page_num[0] == 0:
        return
    if not os.path.exists(json_file):
        with open(json_file, 'w', encoding='utf-8') as jf:
            jf.write(json.dumps(tmpjson, indent=4, ensure_ascii=False))
    if not next_page:
        return
    if page_num[0] < 2:
        return
    for new_page in range(2, page_num[0] + 1):
        down_year_week(yr, wk, new_page, savedir, next_page=False)


def read_parse_data_to_excel(wp, rawdir):
    raw_jsonfiles = FileClass.get_full_filename_by_suffixes(rawdir, 'json')

    # Data structure
    # {YYYY: {WEEK: {'river': {'River1': {'Station1': {'cross_section': '',
    #                                                  'pH': '', ...
    #                                                 }
    #                                    }
    #                         }
    #               }
    #        }
    # }
    #
    szdata = dict()

    for jsonfile in raw_jsonfiles:
        try:
            with open(jsonfile, 'r', encoding='utf-8') as jf:
                json_data = json.load(jf)
        except:
            continue
        json_data = UtilClass.decode_strs_in_dict(json_data)

        if 'docs' not in json_data:
            pass
        for rec in json_data['docs']:
            if 's1' not in rec:
                continue
            rec = UtilClass.decode_strs_in_dict(rec)
            tmpyear = rec['s4']
            tmpweek = rec['s5']
            tmpriver = rec['s1'].replace(' ', '')
            tmpriver = tmpriver.replace('、', '')

            tmpstation = rec['s2'].replace(' ', '')
            tmpstation = tmpstation.replace('（', '(')
            tmpstation = tmpstation.replace('）', ')')
            tmpstation = tmpstation.replace('　', '')
            tmpstation = tmpstation.replace('－', '-')

            tmpcross = rec['s3'].replace(' ', '')
            tmpcross = tmpcross.replace('（', '(')
            tmpcross = tmpcross.replace('）', ')')
            tmpcross = tmpcross.replace('　', '')
            tmpcross = tmpcross.replace('－', '-')
            tmpcross = tmpcross.replace('交接断面', '交界断面')

            szdata.setdefault(tmpyear, dict())  # year
            szdata[tmpyear].setdefault(tmpweek, dict())
            szdata[tmpyear][tmpweek].setdefault(tmpriver, dict())
            szdata[tmpyear][tmpweek][tmpriver].setdefault(tmpstation, {'s3': tmpcross,
                                                                       'f1': rec['f1'],
                                                                       'f2': rec['f2'],
                                                                       'f3': rec['f3'],
                                                                       'f4': rec['f4'],
                                                                       'f5': rec['f5'],
                                                                       'f6': rec['f6'],
                                                                       's8': rec['s8'],
                                                                       's9': rec['s9'],
                                                                       's10': rec['s10']})
    # print(szdata)
    years = sorted(szdata.keys())
    out_name = 'fujian_shuizhi_zhoubao_%d%02d-%d%02d.xls' % (years[0],
                                                             sorted(szdata[years[0]].keys())[0],
                                                             years[-1],
                                                             sorted(szdata[years[-1]].keys())[-1])

    dataitems = list()
    header_names = [SEL_FIELDS[orgname] for orgname in TITLES]
    dataitems.append(header_names)
    for outyear in years:
        for outweek in sorted(szdata[outyear].keys()):
            for outriver, river_value in iteritems(szdata[outyear][outweek]):
                for outstation, station_value in iteritems(szdata[outyear][outweek][outriver]):
                    curitem = [outyear, outweek, outriver, outstation]
                    for i in range(4, len(TITLES)):
                        curitem.append(station_value[TITLES[i]])
                    dataitems.append(curitem)

    out_xls = wp + os.sep + out_name
    write_data_to_xls(dataitems, out_xls)


if __name__ == "__main__":
    wp = 'D:\\tmp\\fujian_shuizhi_zhoubao'
    rawdir = wp + os.sep + 'raw_data'
    UtilClass.mkdir(rawdir)

    year_range = [2000, 2020]  # e.g., [2019], [2000, 2020]
    week_range = [1, 52]  # e.g., [1], [1,30], default is [1, 52] for entire year

    if len(year_range) == 1:
        year_range = [year_range[0], year_range[0]]
    if len(week_range) == 1:
        week_range = [week_range[0], week_range[0]]

    # Download and save as JSON-formatted files
    for year in range(year_range[0], year_range[1] + 1):
        for week in range(week_range[0], week_range[1] + 1):
            print('Downloading year: %d, week: %d...' % (year, week))
            down_year_week(year, week, 1, rawdir, next_page=True)

    # Read and parse to Excel files
    read_parse_data_to_excel(wp, rawdir)

#! /usr/bin/env python
# coding=utf-8

import urllib2
import os
import sys
import fileinput
import shutil
import time

from pygeoc.utils import UtilClass, StringClass


def downloadByUrl(curUrl, filePath):
    if os.path.exists(filePath):
        return
    try:
        f = urllib2.urlopen(curUrl)
        data = f.read()
        with open(filePath, "wb") as code:
            code.write(data)
        return True
    except Exception:
        return False


def read_data_items_from_txt(txt_file):
    """Read data items include title from text file, each data element are split by TAB or COMMA.
       Be aware, the separator for each line can only be TAB or COMMA, and COMMA is the recommended.
    Args:
        txt_file: full path of text data file
    Returns:
        2D data array
    """
    data_items = list()
    with open(txt_file, 'r') as f:
        for line in f:
            str_line = line.strip()
            if str_line != '' and str_line.find('#') < 0:
                line_list = StringClass.split_string(str_line, ['\t'])
                if len(line_list) <= 1:
                    line_list = StringClass.split_string(str_line, [','])
                data_items.append(line_list)
    return data_items


def download_m3u8_resolution(ws, furl, name):
    dst_url = furl
    dst_file = ws + os.sep + 'pre_%s.m3u8' % name
    downloadByUrl('%s/output.m3u8' % furl, dst_file)
    if not os.path.exists(dst_file):
        return None
    with open(dst_file, 'r') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            line = line.strip()
            if '102400' in line and len(lines) > idx:
                dst_url += '/%s' % lines[idx + 1]
                rno = dst_url.rfind('/')
                return dst_url[:rno]
        print("Not found!")
        return None


def download_actual_m3u8(ws, furl, name):
    dst_file = ws + os.sep + '%s.m3u8' % name
    downloadByUrl('%s/output.m3u8' % furl, dst_file)
    if not os.path.exists(dst_file):
        return None
    # replace "/mykey.key" with "mykey.key"
    for i, line in enumerate(fileinput.input(dst_file, inplace=1)):
        if '/mykey.key' in line:
            sys.stdout.write(line.replace('/mykey.key', 'mykey.key'))
        else:
            sys.stdout.write(line)
    return dst_file


def download_ts_files(ws, dstf, baseurl):
    urls = list()
    with open(dstf, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if '.ts' not in line:
                continue
            tmpurl = '%s/%s' % (baseurl, line)
            urls.append(tmpurl)
            try_time = 0
            while try_time <= 3:
                if not downloadByUrl(tmpurl, ws + os.sep + line):
                    try_time += 1
                    time.sleep(0.1)
                else:
                    break


if __name__ == '__main__':
    # workspace = r'/home/zhulj/test/zhongYeWangXiao'
    workspace = r'D:\test\ts'
    fname_urls = workspace + os.sep + 'buchong.txt'
    key_file = workspace + os.sep + 'mykey.key'
    ffmpeg_bin = r'c:\ffmpeg\bin\ffmpeg'

    furls = read_data_items_from_txt(fname_urls)
    comb_dir = workspace + os.sep + 'combination'
    if not os.path.isdir(comb_dir):
        os.mkdir(comb_dir)
    for fdir, fname, furl in furls:
        print('downloading %s...' % fname)
        tmp_ws = workspace + os.sep + fdir
        if not os.path.isdir(tmp_ws):
            os.mkdir(tmp_ws)
        tmp_comb_dir = comb_dir + os.sep + fdir
        if not os.path.isdir(tmp_comb_dir):
            os.mkdir(tmp_comb_dir)
        tmp_ts_dir = tmp_ws + os.sep + fname
        if not os.path.isdir(tmp_ts_dir):
            os.mkdir(tmp_ts_dir)

        dstUrl = download_m3u8_resolution(tmp_ts_dir, furl, fname)
        if dstUrl is None:
            print("%s failed, can not download pre_output.m3u8\n" % fname)
            continue
        print(dstUrl)

        dstFile = download_actual_m3u8(tmp_ts_dir, dstUrl, fname)
        if dstFile is None:
            print("%s failed, can not download actual output.m3u8\n" % fname)
            continue
        print(dstFile)

        shutil.copy(key_file, tmp_ts_dir + os.sep + 'mykey.key')
        download_ts_files(tmp_ts_dir, dstFile, dstUrl)

        UtilClass.run_command([ffmpeg_bin,
                               '-allowed_extensions', 'ALL',
                               '-i', '%s/%s.m3u8' % (tmp_ts_dir, fname),
                               '-bsf:a', 'aac_adtstoasc',
                               '-vcodec', 'copy',
                               '-c', 'copy',
                               '-crf', '50', '%s/%s.mp4' % (tmp_comb_dir, fname)])
        time.sleep(10)

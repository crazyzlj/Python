#! /usr/bin/env python
# coding=utf-8
# Func. : Create and Update Database of SURF_CLI_CHN_MUL_DAY_V3.0 from data.cma.cn
# Author: Liangjun Zhu
# Date  : 2016-4-10
# Revision: 2017-1-4
#           2018-6-22  1. Fix datetime issue.
#                      2. Add missing elements, i.e., PRS and GST
#                      3. Add missing data 196903-196912.
# Email : zlj@lreis.ac.cn
# Blog  : http://zhulj.net/python/2016/04/11/Constructing-SURF_CLI_CHN_MUL_DAY_V3.0-database.html

import time

import os
import sqlite3
import datetime

# ----------------------SQLite related functions  ----------------------------------------------#
# ------------http://blog.csdn.net/cdnight/article/details/45332895-----------------------------#
# Global variable
SHOW_SQL = False


def get_conn(path):
    """
    get connection of Sqlite
    :param path: path of Sqlite database
    """
    conn = sqlite3.connect(path)
    if os.path.exists(path) and os.path.isfile(path):
        # print('database in hardware :[{}]'.format(path))
        return conn
    else:
        conn = None
        # print('database in memory :[:memory:]')
        return sqlite3.connect(':memory:')


def get_cursor(conn):
    """
    get cursor of current connection
    :param conn: connection of Sqlite
    """
    if conn is not None:
        return conn.cursor()
    else:
        return get_conn('').cursor()


def drop_table(conn, table):
    """
    Drop table if exists. Be careful to use!
    :param conn:
    :param table:
    :return:
    """
    if table is not None and table != '':
        sql = 'DROP TABLE IF EXISTS ' + table
        if SHOW_SQL:
            print('execute sql: [{}]'.format(sql))
        cu = get_cursor(conn)
        cu.execute(sql)
        conn.commit()
        print('drop table [{}] succeed!'.format(table))
        close_all(conn, cu)
    else:
        print('the [{}] is empty or equal None!'.format(table))


def close_all(conn, cu):
    """
    close connection and cursor of Sqlite
    :param conn: connection of Sqlite
    :param cu: cursor of conn
    """
    try:
        if cu is not None:
            cu.close()
    finally:
        if cu is not None:
            cu.close()


def saveRecord(conn, sql, data):
    """
    save records to database
    :param conn: connection of Sqlite
    :param sql: sql sentence
    :param data: array data
    """
    if sql is not None and sql != '':
        if data is not None:
            cu = get_cursor(conn)
            cu.execute(sql, data)
            # conn.commit()
            cu.close()
            # close_all(conn,cu)
    else:
        print('the [{}] is empty or equal None!'.format(sql))


def updateRecord(conn, sql, data):
    """
    Update one record
    :param conn:
    :param sql:
    :param data:
    :return:
    """
    if sql is not None and sql != '':
        if data is not None:
            cu = get_cursor(conn)
            if SHOW_SQL:
                print('execute sql: [{}], parameter: {}'.format(sql, data))
            cu.execute(sql, data)
            # conn.commit()
            # close_all(conn, cu)
    else:
        print('the [{}] is empty or equal None!'.format(sql))


def fetchOneRecord(conn, sql, data):
    """
    Query one record
    :param conn:
    :param sql:
    :param data: should be an array
    :return:
    """
    if sql is not None and sql != '':
        if data is not None:
            if not isinstance(data, list) and not isinstance(data, tuple):
                data = (data,)
            cu = get_cursor(conn)
            if SHOW_SQL:
                print('execute sql: [{}], parameter: {}'.format(sql, data))
            cu.execute(sql, data)
            r = cu.fetchall()
            if len(r) > 0:
                return True
            else:
                return False
        else:
            print('the [{}] equal None!'.format(data))
            return False
    else:
        print('the [{}] is empty or equal None!'.format(sql))
        return False


def createTable(sqlStr, conn):
    """
    create table of database
    :param sqlStr: sql sentence
    :param conn: connection of Sqlite
    """
    if sqlStr is not None and sqlStr != '':
        cu = get_cursor(conn)
        if SHOW_SQL:
            print('execute sql: [{}]'.format(sqlStr))
        cu.execute(sqlStr)
        conn.commit()
        close_all(conn, cu)
    else:
        print('the [{}] is empty or equal None!'.format(sqlStr))


def writeClimateStationToDatabase(allStationInfo, dbpath):
    """
    write climate station information to database as table named 'stationInfo'
    :param allStationInfo: station information directionary
    :param dbpath: path of Sqlite database
    """
    print('Write station information to database...')
    conn = sqlite3.connect(dbpath)
    # create station information table
    stationInfoTab = 'stationInfo'
    create_station_info_tab_sql = '''CREATE TABLE IF NOT EXISTS %s (
                        stID varchar(5) PRIMARY KEY NOT NULL,
                        lat float DEFAULT NULL,
                        lon float DEFAULT NULL,
                        alti int DEFAULT NULL
                        )''' % stationInfoTab
    createTable(create_station_info_tab_sql, conn)
    save_stationInfo_sql = '''INSERT INTO %s values (?,?,?,?)''' % stationInfoTab
    fetchone_sql = 'SELECT * FROM %s WHERE stID = ? ' % stationInfoTab
    for info, sdata in list(allStationInfo.items()):
        # If the current station exists, continue to next one.
        if fetchOneRecord(conn, fetchone_sql, sdata.StationID):
            continue
        # If the current station does not exist, then insert its information.
        dataRow = [sdata.StationID, sdata.lat, sdata.lon, sdata.alti]
        saveRecord(conn, save_stationInfo_sql, dataRow)
    conn.commit()
    conn.close()


def writeClimateDataToDatabase(allClimData, dbpath):
    """
    write climate data to database
    :param allClimData: climate data of all stations' dictionary
    :param dbpath: path of Sqlite database
    """
    print('Write climate data to database...')
    conn = sqlite3.connect(dbpath)
    count = 1
    for station in allClimData:
        print('---%d / %d, station ID: %s...' % (count, len(allClimData),
                                                 allClimData[station].StationID))
        count += 1
        stationTabName = 'S' + allClimData[station].StationID
        # create table if not exists.
        create_climdata_tab_sql = '''CREATE TABLE IF NOT EXISTS %s (
                        stID varchar(5) NOT NULL,
                        date datetime DEFAULT NULL,
                        avgPRS int DEFAULT 9999,
                        maxPRS int DEFAULT 9999,
                        minPRS int DEFAULT 9999,
                        avgTEM int DEFAULT 9999,
                        maxTEM int DEFAULT 9999,
                        minTEM int DEFAULT 9999,
                        avgRHU int DEFAULT 9999,
                        minRHU int DEFAULT 9999,
                        PRE208 int DEFAULT 9999,
                        PRE820 int DEFAULT 9999,
                        PRE int DEFAULT 9999,
                        smEVP int DEFAULT 9999,
                        lgEVP int DEFAULT 9999,
                        avgWIN int DEFAULT 9999,
                        maxWIN int DEFAULT 9999,
                        maxWINASP int DEFAULT 9999,
                        extWIN int DEFAULT 9999,
                        extWINASP int DEFAULT 9999,
                        SSD int DEFAULT 9999,
                        avgGST int DEFAULT 9999,
                        maxGST int DEFAULT 9999,
                        minGST int DEFAULT 9999
                        )''' % stationTabName
        createTable(create_climdata_tab_sql, conn)
        # insert station information
        curClimateData = allClimData[station]
        fetchone_sql = 'SELECT * FROM %s WHERE stID = ? AND date = ?' % stationTabName
        update_sql = '''UPDATE %s SET avgPRS = ?, maxPRS = ?, minPRS = ?, \
                        avgTEM = ?, maxTEM = ?, minTEM = ?, avgRHU = ?, minRHU = ?,\
                        PRE208 = ?, PRE820 = ?, PRE = ?, \
                        smEVP = ?, lgEVP = ?, avgWIN = ?, maxWIN = ?,\
                        maxWINASP = ?, extWIN = ?, extWINASP = ?, SSD = ?,\
                        avgGST = ?, maxGST = ?, minGST = ? WHERE stID = ? AND date = ?''' \
                     % stationTabName
        save_sql = '''INSERT INTO %s values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''' % stationTabName
        for i in range(curClimateData.count):
            # If the current station record exists, then update it, else insert one.
            uniqueitem = [curClimateData.StationID, curClimateData.date[i]]
            dataRow = [curClimateData.StationID, curClimateData.date[i],
                       curClimateData.avgPRS[i], curClimateData.maxPRS[i], curClimateData.minPRS[i],
                       curClimateData.avgTEM[i], curClimateData.maxTEM[i], curClimateData.minTEM[i],
                       curClimateData.avgRHU[i], curClimateData.minRHU[i],
                       curClimateData.PRE208[i], curClimateData.PRE820[i],
                       curClimateData.PRE[i], curClimateData.smEVP[i], curClimateData.lgEVP[i],
                       curClimateData.avgWIN[i], curClimateData.maxWIN[i],
                       curClimateData.maxWINASP[i],
                       curClimateData.extWIN[i], curClimateData.extWINASP[i],
                       curClimateData.SSD[i],
                       curClimateData.avgGST[i], curClimateData.maxGST[i], curClimateData.minGST[i]]
            # print(dataRow)
            if fetchOneRecord(conn, fetchone_sql, uniqueitem):
                updateRecord(conn, update_sql, dataRow[2:] + uniqueitem)
                continue
            saveRecord(conn, save_sql, dataRow)
    conn.commit()
    conn.close()


# -----------------------------------------------------------------------------------------------#
class climateStation:
    """
    class of climate station
    :method: init(ID, lat, lon, alti)
    :method: printStation()
    """

    def __init__(self, id='', lat=9999., lon=9999., alti=9999.):
        self.StationID = id  # 5 digits
        self.lat = lat  # latitude, ORIGIN: up to 5 digits, the format is degree+minute ==> float degree
        self.lon = lon  # longitude, ORIGIN: up to 5 digits, the format is degree+minute ==> float degree
        self.alti = alti  # altitude, ORIGIN: unit 0.1 meter

    def printStation(self):
        print('%s, %.3f, %.3f, %.1f' % (self.StationID, self.lat, self.lon, self.alti))


class climateStation2:
    """
    class of climate station2, in case of various station information, such as different elevations
    :method: init(ID, lat, lon, alti)
    :method: printStation()
    """

    def __init__(self, id='', lat=9999., lon=9999., alti=9999.):
        self.count = 1
        self.StationID = id  # 5 digits
        self.lat = [lat]
        self.lon = [lon]
        self.alti = [alti]

    def printStation(self):
        print('%s, %s, %s, %s' % (self.StationID, self.lat, self.lon, self.alti))


class climateFeatures(climateStation):
    """
    class of climate feature, totally 22 attributes!
    :method: init(ID, lat, lon, alti)
    :method: initValues()
    :method: assignValuesByFtCode(idx, ftCode, ClimValues)
    :method: check()
    :method: printFeature()
    """

    def __init__(self, id='', lat=9999., lon=9999., alti=9999.):
        climateStation.__init__(self, id, lat, lon, alti)
        self.count = 0
        self.date = list()  # UTC+08:00 date, i.e., Beijing time.
        self.avgPRS = list()  # average pressure of the day, ORIGIN: unit 0.1 hPa
        self.maxPRS = list()  # maximum pressure of the day, ORIGIN: unit 0.1 hPa
        self.minPRS = list()  # minimum pressure of the day, ORIGIN: unit 0.1 hPa
        self.avgTEM = list()  # average temperature of the day, ORIGIN: unit 0.1 degree
        self.maxTEM = list()  # maximum temperature of the day
        self.minTEM = list()  # minimum temperature of the day
        self.avgRHU = list()  # average relative humidity, unit 1%
        self.minRHU = list()  # minimum relative humidity, nuit 1%
        self.PRE208 = list()  # precipitation from 20:00 to 8:00
        self.PRE820 = list()  # precipitation from 8:00 to 20:00
        self.PRE = list()  # precipitation from 20:00 to 20:00, ORIGIN: unit 0.1 mm
        self.smEVP = list()  # small evaporation, ORIGIN: unit 0.1 mm
        self.lgEVP = list()  # large evaporation, ORIGIN: unit 0.1 mm
        self.avgWIN = list()  # mean wind speed, ORIGIN: unit 0.1 m/s
        self.maxWIN = list()  # maximum wind speed, ORIGIN: unit 0.1 m/s
        self.maxWINASP = list()  # aspect of maximum wind speed
        self.extWIN = list()  # extreme wind speed
        self.extWINASP = list()  # aspect of extreme wind speed
        self.SSD = list()  # sunshine duration hours, ORIGIN: 0.1 hour
        self.avgGST = list()  # average ground surface temperature of the day, ORIGIN: 0.1 degree
        self.maxGST = list()  # maximum ground surface temperature of the day, ORIGIN: 0.1 degree
        self.minGST = list()  # minimum ground surface temperature of the day, ORIGIN: 0.1 degree

    def initValues(self):
        self.count += 1
        self.avgPRS.append(9999)
        self.maxPRS.append(9999)
        self.minPRS.append(9999)
        self.avgTEM.append(9999)
        self.maxTEM.append(9999)
        self.minTEM.append(9999)
        self.avgRHU.append(9999)
        self.minRHU.append(9999)
        self.PRE208.append(9999)
        self.PRE820.append(9999)
        self.PRE.append(9999)
        self.smEVP.append(9999)
        self.lgEVP.append(9999)
        self.avgWIN.append(9999)
        self.maxWIN.append(9999)
        self.maxWINASP.append(9999)
        self.extWIN.append(9999)
        self.extWINASP.append(9999)
        self.SSD.append(9999)
        self.avgGST.append(9999)
        self.maxGST.append(9999)
        self.minGST.append(9999)

    def assignValuesByFtCode(self, idx, ftCode, ClimValues):
        # ['PRS', 'TEM', 'RHU', 'PRE', 'EVP', 'WIN', 'SSD', 'GST']
        if ftCode == 'PRS' and len(ClimValues) == 3:
            self.avgPRS[idx] = ClimValues[0]
            self.maxPRS[idx] = ClimValues[1]
            self.minPRS[idx] = ClimValues[2]
        elif ftCode == 'TEM' and len(ClimValues) == 3:
            self.avgTEM[idx] = ClimValues[0]
            self.maxTEM[idx] = ClimValues[1]
            self.minTEM[idx] = ClimValues[2]
        elif ftCode == 'RHU' and len(ClimValues) == 2:
            self.avgRHU[idx] = ClimValues[0]
            self.minRHU[idx] = ClimValues[1]
        elif ftCode == 'PRE' and len(ClimValues) == 3:
            self.PRE208[idx] = ClimValues[0]
            self.PRE820[idx] = ClimValues[1]
            self.PRE[idx] = ClimValues[2]
        elif ftCode == 'EVP' and len(ClimValues) == 2:
            self.smEVP[idx] = ClimValues[0]
            self.lgEVP[idx] = ClimValues[1]
        elif ftCode == 'WIN' and len(ClimValues) == 5:
            self.avgWIN[idx] = ClimValues[0]
            self.maxWIN[idx] = ClimValues[1]
            self.maxWINASP[idx] = ClimValues[2]
            self.extWIN[idx] = ClimValues[3]
            self.extWINASP[idx] = ClimValues[4]
        elif ftCode == 'SSD' and len(ClimValues) == 1:
            self.SSD[idx] = ClimValues[0]
        elif ftCode == 'GST' and len(ClimValues) == 3:
            self.avgGST[idx] = ClimValues[0]
            self.maxGST[idx] = ClimValues[1]
            self.minGST[idx] = ClimValues[2]
        else:
            exit(1)

    def check(self):
        if self.count == len(self.date) \
                == len(self.avgPRS) == len(self.maxPRS) == len(self.minPRS) \
                == len(self.maxTEM) == len(self.minTEM) == len(self.avgTEM) \
                == len(self.avgRHU) == len(self.minRHU) \
                == len(self.PRE208) == len(self.PRE820) == len(self.PRE) \
                == len(self.smEVP) == len(self.lgEVP) \
                == len(self.avgWIN) == len(self.maxWIN) == len(self.maxWINASP) \
                == len(self.extWIN) == len(self.extWINASP) == len(self.SSD) \
                == len(self.avgGST) == len(self.maxGST) == len(self.minGST):
            return True
        else:
            return False

    def printFeature(self):
        print('%s, lat=%.3f, lon=%.3f, alti=%.1f, count=%d, date=%s, PRS=%s, TEM=%s,'
              ' RHU=%s, PRE=%s, EVP=%s, WIN=%s, SSD=%s, GST=%s' %
              (self.StationID, self.lat, self.lon, self.alti, self.count, self.date,
               self.avgPRS, self.avgTEM, self.avgRHU, self.PRE,
               self.lgEVP, self.avgWIN, self.SSD, self.avgGST))


#### Strip and split ####
def StripStr(str):
    """
    Remove space(' ') and indent('\t') at the begin and end of the string
    """
    oldStr = ''
    newStr = str
    while oldStr != newStr:
        oldStr = newStr
        newStr = oldStr.strip('\t')
        newStr = newStr.strip(' ')
    return newStr


def SplitStr(str, spliter=None):
    """
    Split string by spliter space(' ') and indent('\t') as default
    """
    spliters = [' ', '\t']
    if spliter is not None:
        spliters.append(spliter)
    destStrs = list()
    srcStrs = [str]
    while True:
        oldDestStrs = srcStrs[:]
        for s in spliters:
            for srcS in srcStrs:
                tempStrs = srcS.split(s)
                for tempS in tempStrs:
                    tempS = StripStr(tempS)
                    if tempS != '':
                        destStrs.append(tempS)
            srcStrs = destStrs[:]
            destStrs = list()
        if oldDestStrs == srcStrs:
            destStrs = srcStrs[:]
            break
    return destStrs


#########################
def listTxtPaths(path):
    """
    list text paths in current path
    """
    tempFiles = os.listdir(path)
    txtPaths = list()
    suffixs = ['txt', 'TXT']
    for s in tempFiles:
        if s.split(".")[-1] in suffixs:
            txtPaths.append(path + os.sep + s)
    return tempFiles, txtPaths


def MatchFeature(path):
    """
    return ftcode in current text path
    """
    ftCodes = ['PRS', 'TEM', 'RHU', 'PRE', 'EVP', 'WIN', 'SSD', 'GST']
    # PRS: pressure, TEM: temperature, RHU: relative humidity, PRE: precipitation,
    # EVP: evaporation, WIN: wind, SSD: sunshine duration, GST: groud surface temperature
    tempStrs = path.split('-')
    for s in tempStrs:
        if s in ftCodes:
            return s
    return None


def sparseClimateItem(itemStr, climFtCls, ftCode):
    """
    sparse climate item
    """
    ftCodes = ['PRS', 'TEM', 'RHU', 'PRE', 'EVP', 'WIN', 'SSD', 'GST']
    ftValueNum = [3, 3, 2, 3, 2, 5, 1, 3]  # climate values start from column 8, i.e., index = 7
    curYear = int(itemStr[4])
    curMonth = int(itemStr[5])
    curDay = int(itemStr[6])
    curHour = 20  # UTC+08:00
    curDate = datetime.datetime(curYear, curMonth, curDay, curHour)
    climValues = list()
    ftIdx = ftCodes.index(ftCode)
    ftNum = ftValueNum[ftIdx]
    for i in range(ftNum):
        climValues.append(int(itemStr[7 + i]))
    curIdx = -9999
    if curDate in climFtCls.date:
        curIdx = climFtCls.date.index(curDate)
    else:
        climFtCls.date.append(curDate)
        climFtCls.initValues()
        curIdx = climFtCls.count - 1
    if curIdx != -9999:
        climFtCls.assignValuesByFtCode(curIdx, ftCode, climValues)


def latlon(latlonStr):
    """
    from latlonStr string to calculate latitude or longitude
    """
    minute = float(latlonStr[-2:])
    degree = float(latlonStr[0:len(latlonStr) - 2])
    return degree + minute / 60.


def readClimateTxtData(txtPath):
    """
    read climate data from text file
    """
    print('Read climate data...')
    totNum = 0
    curNum = 1
    for root, dirs, files in os.walk(txtPath):
        totNum = len(files)
    txtFileName, txtPathList = listTxtPaths(txtPath)
    all_stat_clim_data = dict()  ##  format: StationID: climateFeatures
    all_station_info = dict()  ##  format: StationID: climateStation
    ftCodes = ['PRS', 'TEM', 'RHU', 'PRE', 'EVP', 'WIN', 'SSD', 'GST']
    fieldCols = [13, 13, 11, 13, 11, 17, 9, 13]
    for txt in txtPathList:
        print('--- %d / %d, read climate data file: %s...' % (
            curNum, totNum, txtFileName[txtPathList.index(txt)]))
        curNum += 1
        ftCode = MatchFeature(txt)
        if ftCode is not None:
            # print ftCode
            curf = open(txt)
            for line in curf:
                curClimItem = SplitStr(StripStr(line.split('\n')[0]))
                if len(curClimItem) == fieldCols[ftCodes.index(ftCode)]:
                    # print(curClimItem)
                    if curClimItem[0] not in all_station_info.keys():
                        all_stat_clim_data[curClimItem[0]] = climateFeatures(curClimItem[0],
                                                                             latlon(curClimItem[1]),
                                                                             latlon(curClimItem[2]),
                                                                             int(curClimItem[3]))
                        all_station_info[curClimItem[0]] = climateStation(curClimItem[0],
                                                                          latlon(curClimItem[1]),
                                                                          latlon(curClimItem[2]),
                                                                          int(curClimItem[3]))
                    sparseClimateItem(curClimItem, all_stat_clim_data[curClimItem[0]], ftCode)
            curf.close()
    # print(len(all_stat_clim_data))
    # for item in all_stat_clim_data.keys():
    #     print(all_stat_clim_data[item].printFeature())
    #     print(all_stat_clim_data[item].check())
    print('Climate data read finished!')
    return all_station_info, all_stat_clim_data


def readClimateTxtDataForStations(txtPath):
    """
    read stations' information from climate text file
    """
    print('Read Stations information...')
    totNum = 0
    curNum = 1
    for root, dirs, files in os.walk(txtPath):
        totNum = len(files)
    txtFileName, txtPathList = listTxtPaths(txtPath)
    all_station_info = dict()  ##  format: StationID: climateStation2
    ftCodes = ['PRS', 'TEM', 'RHU', 'PRE', 'EVP', 'WIN', 'SSD', 'GST']
    fieldCols = [13, 13, 11, 13, 11, 17, 9, 13]
    for txt in txtPathList:
        print('--- %d / %d, read climate data file: %s...' % (
            curNum, totNum, txtFileName[txtPathList.index(txt)]))
        curNum += 1
        ftCode = MatchFeature(txt)
        if ftCode is not None:
            # print(ftCode)
            curf = open(txt)
            for line in curf:
                curClimItem = SplitStr(StripStr(line.split('\n')[0]))
                if len(curClimItem) == fieldCols[ftCodes.index(ftCode)]:
                    # print curClimItem
                    if curClimItem[0] not in all_station_info.keys():
                        all_station_info[curClimItem[0]] = climateStation2(curClimItem[0],
                                                                           curClimItem[1],
                                                                           curClimItem[2],
                                                                           curClimItem[3])
                    else:
                        preInfo = all_station_info[curClimItem[0]]
                        curLat = curClimItem[1]
                        curLon = curClimItem[2]
                        curAlti = curClimItem[3]
                        preLat = preInfo.lat
                        preLon = preInfo.lon
                        preAlti = preInfo.alti
                        flag = True
                        for i in range(preInfo.count):
                            if preLat[i] == curLat and preLon[i] == curLon and \
                                    preAlti[i] == curAlti:
                                flag = False
                        if flag:
                            preLat.append(curLat)
                            preLon.append(curLon)
                            preAlti.append(curAlti)
                            preInfo.lat = preLat
                            preInfo.lon = preLon
                            preInfo.alti = preAlti
                            preInfo.count = len(preInfo.lat)
            curf.close()

    print('Climate stations information read finished!')
    # for item in all_station_info.keys():
    #      print(all_station_info[item].printStation())
    return all_station_info


def writeClimateStationToTxt(stationInfos, txtPath):
    f = open(txtPath, "w")
    title = 'stationID,count,lat,lon,alti\n'
    f.write(title)
    for items in stationInfos.keys():
        itemsStr = items + ',' + str(stationInfos[items].count) + ','
        curLat = stationInfos[items].lat
        curLon = stationInfos[items].lon
        curAlti = stationInfos[items].alti
        for i in range(stationInfos[items].count):
            writeItem = itemsStr + str(curLat[i]) + ',' + str(curLon[i]) + \
                        ',' + str(curAlti[i]) + '\n'
            f.write(writeItem)
    f.close()


def readClimateStationTxt(txtpath):
    f = open(txtpath)
    station = list()
    i = 0
    l = 0
    for line in f:
        strs = line.split(',')
        print(strs)
        l += 1
        if l == 10:
            break
        if [strs[0], strs[1]] not in station:
            station.append([strs[0], strs[1]])
            i += 1
    f.close()
    # print(station)


if __name__ == '__main__':
    SRC_DATA_PATH = r'C:\z_data\common_GIS_Data\SURF_CLI_CHN_MUL_DAY_V3.0\download'
    SQLITE_DB_PATH = r'C:\z_data\common_GIS_Data\SURF_CLI_CHN_MUL_DAY_V3.0\test.db'
    startT = time.time()
    ALL_STATION_INFO, ALL_STATION_DATA = readClimateTxtData(SRC_DATA_PATH)
    writeClimateStationToDatabase(ALL_STATION_INFO, SQLITE_DB_PATH)
    writeClimateDataToDatabase(ALL_STATION_DATA, SQLITE_DB_PATH)
    endT = time.time()
    cost = endT - startT
    print('All mission done, time-consuming: ' + str(cost) + ' s\n')

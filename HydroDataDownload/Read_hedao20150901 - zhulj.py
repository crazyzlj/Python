# coding=utf-8
#本程序从http://shangqing.wswj.net/TYFW/InfoQuery/ZhaBa.aspx下载安徽省闸坝水情信息
# Created by Liangjun Zhu 201412
# Modified by Tengfei Wei 20150413

import httplib,string,sys,time,urllib,os,datetime
from cStringIO import StringIO
from pyquery import PyQuery as pq
import sqlite3
import gzip
from multiprocessing.dummy import Pool as ThreadPool
from collections import OrderedDict

#下载网页的方法
def downHTML(TargetPage,ViewState,EventValidation):
    #加参数
    params = urllib.urlencode({'__EVENTTARGET':'anpPage',
                               '__EVENTARGUMENT':TargetPage,
                               '__LASTFOCUS':'',
                               '__VIEWSTATE':ViewState,
                               '__EVENTVALIDATION':EventValidation,
                               #新加参数
                               '__VIEWSTATEGENERATOR':'8963DA15',
                               #新添加的参数
                               'anpPage_input':'4',
                               'DdlPageSize':'27'
                               })
    headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               "Accept-Encoding":"gzip,deflate",
               "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
               "Cache-Control":"max-age=0",
               "Connection":"keep-alive",
               "Content-Length":len(params),
               "Content-Type":"application/x-www-form-urlencoded",
               "Cookie":"ASP.NET_SessionId=3bote2o4m4xazzljy20ttmf2; a4046_pages=2; a4046_times=3",
               "Host":"shangqing.wswj.net",
               "Origin":"http://shangqing.wswj.net",
               "Referer":"http://shangqing.wswj.net/TYFW/InfoQuery/HeDao.aspx",
               "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36"
               }
    #print params,headers
    conn = httplib.HTTPConnection("61.191.22.157:80")
    conn.request(method="POST",
                 #网址修改
                 url="http://shangqing.wswj.net/TYFW/InfoQuery/HeDao1.aspx",
                 body=params,
                 headers=headers)
    response = conn.getresponse()
    #print response.status
    if response.status == 200:
        Res = response.read()
        html = gzip.GzipFile(fileobj=StringIO(Res), mode="r").read()
        #print html
        return html
        conn.close()
        print "Get Response HTML Content Succeed!"
    else:
        conn.close()
        time.sleep(20)
        return downHTML(TargetPage,ViewState,EventValidation)


#将打开的网页页面保存为txt格式
def saveCurFile(htmlContent,TargetPage,storePath):
    htmlFile = storePath + os.sep + 'Page' + str(TargetPage) + '.txt'
    f = open(htmlFile,'w')
    f.write(htmlContent)
    f.close
    return htmlFile

#----------------------数据或相关操作的主要方法----------------------------------------------#
#获取游标
def get_cursor(conn):
    if conn is not None:
        return conn.cursor()
    else:
        return get_conn('').cursor()
#关闭所有
def close_all(conn, cu):
    try:
        if cu is not None:
            cu.close()
    finally:
        if cu is not None:
            cu.close()
#保存记录
def saveRecord(conn, sql, data):
    if sql is not None and sql != '':
        if data is not None:
            cu = get_cursor(conn)
            cu.execute(sql,data)
            #conn.commit()
        cu.close()
        #close_all(conn,cu)
    else:
        print ('the [{}] is empty or equal None!'.format(sql))
#存入数据库中
def writeDatabase(workspace,storePath,ident):
    #名称需要修改
    dbFile = workspace + 'hedao.db'
    tableName = 'hedao' + str(ident)
    create_table_sql = '''CREATE TABLE IF NOT EXISTS %s (
                        stID varchar(12) NOT NULL,
                        station varchar(30) NOT NULL,
                        cautionLevel float DEFAULT NULL,
                        ensureLevel float DEFAULT NULL,
                        currTime datetime DEFAULT NULL,
                        waterLevel float DEFAULT NULL,
                        flow1 float DEFAULT NULL,
                        averageFlow float DEFAULT NULL,
                        measureMethod varchar(10) DEFAULT NULL
                        )''' % tableName
    # Iterate the HTML files
    os.chdir(storePath) 
    conn = sqlite3.connect(dbFile)
    conn.text_factory = str
        #print create_table_sql
    if create_table_sql is not None and create_table_sql != '':
        #获取游标，上面定义的方法
        cu = get_cursor(conn)
        #执行数据库的语句
        cu.execute(create_table_sql)
        conn.commit()
        close_all(conn, cu)
    else:
        print ('the [{}] is empty or equal None!'.format(create_table_sql))

    for htmlFile in os.listdir("."):
        htmlFile = storePath + os.sep + htmlFile
        f = open(htmlFile,'r')
        htmlContent = f.read().decode("utf-8")
        f.close()
        Q = pq(htmlContent)
        #print Q
        items = Q('tr.Table112_tr1')
        #print items
        save_sql = '''INSERT INTO %s values (?,?,?,?,?,?,?,?,?)''' % tableName
        for i in range(items.length):
            #需要修改
            stID = items.eq(i)('td').eq(1)('a').attr('href').split('stcd=')[1]
            station = items.eq(i)('td').eq(1).text().strip().encode('gbk').replace('\xa1\xa1','').decode('gbk')
            cautionLevel = items.eq(i)('td').eq(2).text()
            ensureLevel = items.eq(i)('td').eq(3).text()
            currTime = datetime.datetime(*(time.strptime(items.eq(i)('td').eq(4).text(),"%Y-%m-%d %H:%M"))[:6])
            waterLevel = items.eq(i)('td').eq(5).text()
            flow1 = items.eq(i)('td').eq(6).text()
            currentwaterLevel = items.eq(i)('td').eq(7).text()
            averageWater = items.eq(i)('td').eq(8).text()
            measureMethod = items.eq(i)('td').eq(9).text()
            dataRow = [stID,station,cautionLevel,ensureLevel,currTime,waterLevel,currentwaterLevel,averageWater,measureMethod]
            saveRecord(conn,save_sql,dataRow)
        print htmlFile + " is inserting to Sqlite database!"
    conn.commit()
    conn.close()
#-----------------------------------------------------------------------------------------------#

#该方法获取页面的参数，有ViewState和EventValidation参数
def getParams(ident):
    #需要修改-------------------（这里面的os.sep是什么意思？？？？？？）
    workspace = 'D:\\WorkSpace\\Download_AnhuiData' + os.sep
    #打开存储在txt文档中的参数信息
    f = open(workspace + 'VIEWSTATE_' + str(ident) + '.txt','r')
    ViewState = f.read()
    print 'Read VIEWSTATE_' + str(ident) + '.txt'
    f.close()
    f = open(workspace + 'EVENTVALIDATION_' + str(ident) + '.txt','r')
    EventValidation = f.read()
    print 'Read EVENTVALIDATION_' + str(ident) + '.txt'
    f.close()
    
    storePath = os.path.join(workspace, 'HTMLs_' + str(ident))
    if not os.path.exists(storePath):
        os.makedirs(storePath)
    return workspace,ViewState,EventValidation,storePath

#声明全局变量
global workspace,ViewState,EventValidation,storePath

#保存网页的页面内容
def ExecuteSaveHTML(ident,TargetPage):
        BeginT = time.time()
        htmlContent = downHTML(TargetPage,ViewState,EventValidation)
        htmlFile = saveCurFile(htmlContent,TargetPage,storePath)
        print "Download Page " + str(TargetPage) + " Finished, Cost %.2f seconds." % float(time.time()-BeginT)

#主函数入口
if __name__ == '__main__':
    #需要修改
    ident = OrderedDict(
             [('xuyi',3)
             ])
    for i in ident.keys():
        try:
            #调用了getParams方法，获取了所有需要的参数，有：workspace,ViewState,EventValidation,storePath
            workspace,ViewState,EventValidation,storePath = getParams(i)
            start = time.time()
            TargetPagesNum = ident[i]
            startDown = time.time()
            for j in range(1,TargetPagesNum+1):
                if(j % 800 == 0):
                    time.sleep(300)
                #执行保存页面
                ExecuteSaveHTML(i,j)  
            print "Download Finished, Cost %.2f seconds." % float(time.time()-startDown)
            startWrite = time.time()
            writeDatabase(workspace,storePath,i)
            print "Written to database Finished, Cost %.2f hours." % (float(time.time()-startWrite)/3600)
        except:
            info = './/ErrorStation.txt'
            f = open(info,'a')
            f.write(i)
            f.write(',')
            f.write(str(ident[i]))
            f.write('\n')
            f.close()
        finally:
            pass   
    print "Stage 1: All missions done, Cost %.2f hours."# % (float(time.time()-start)/3600)
    
    print "now we are ready to deal with the ErrorStation.txt"
    path = './/ErrorStation.txt'
    stations = []
    pages = []
    if (os.path.exists(path)):
        with open('.\ErrorStation.txt','r') as f:
            for line in f.readlines():
                station = line.split(',')[0]
                stations.append(station)
                page = line.split(',')[1]
                page = page.strip()
                pages.append(page)
    print stations,pages
    for i in range(len(stations)):
        try:
            workspace,ViewState,EventValidation,storePath = getParams(stations[i])
            start = time.time()
            TargetPagesNum = int(pages[i])
            startDown = time.time()
            for j in range(1,TargetPagesNum+1):
                if(j%800 == 0):
                    time.sleep(300)
                ExecuteSaveHTML(i,j)
            print "Download Finished, Cost %.2f seconds." % float(time.time()-startDown)
            startWrite = time.time()
            writeDatabase(workspace,storePath,stations[i])
            print "Written to database Finished, Cost %.2f hours." % (float(time.time()-startWrite)/3600)
        except:
            info = './/ErrorStation2.txt'
            f = open(info,'a')
            f.write(stations[i])
            f.write(',')
            f.write(pages[i])
            f.write('\n')
            f.close()
        finally:
            pass
    print 'to be honest,all missions are done!!!'

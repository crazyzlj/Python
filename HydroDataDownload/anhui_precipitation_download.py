#! /usr/bin/env python
#coding=utf-8

import urllib2,httplib,string,sys,time
from xml.etree import ElementTree as xmlTree
def GetYcRainSum(sTime, eTime, stcd, tDivide):
    params = \
        '''<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <GetYcRainSum xmlns="http://tempuri.org/">
          <sdate>%s</sdate>
          <edate>%s</edate>
          <stcd>%s</stcd>
          <DividTime>%s</DividTime>
        </GetYcRainSum>
      </soap:Body>
    </soap:Envelope>'''
    SoapMessage = params % (sTime, eTime, stcd, tDivide)

    def getXML(sTime, eTime, stcd, tDivide):
        try:
            conn = httplib.HTTP("yc.wswj.net")
            conn.putrequest("POST","/ahyc/web_rain/Service.asmx")
            conn.putheader("Accept","*/*")
            conn.putheader("Accept-Encoding","gzip,deflate,sdch")
            conn.putheader("Accept-Language","zh-CN,zh;q=0.8,en;q=0.6")
            conn.putheader("Host","yc.wswj.net")
            conn.putheader("Origin","http://yc.wswj.net")
            #conn.putheader("Connection","keep-alive");
            conn.putheader("Referer","http://yc.wswj.net/ahyc/Main2.swf")
            conn.putheader("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36");
            conn.putheader("Content-Type","text/xml; charset=utf-8")
            conn.putheader("Content-Length", "%d" % len(SoapMessage))
            conn.putheader("SOAPAction","http://tempuri.org/GetYcRainSum")
            conn.putheader("Cookie","ASP.NET_SessionId=suj53q55f3qxjp55anbw0sjg; CNZZDATA3906820=cnzz_eid%3D1809096373-1405232367-http%253A%252F%252Fhfswj.net%252F%26ntime%3D1405302063")
            conn.endheaders()
            conn.send(SoapMessage)
            statuscode, statusmessage, header = conn.getreply()
            print "Response: ",statuscode, statusmessage
            if statuscode == 200:
                #print "Headers: ", header
                Res = conn.getfile().read()
                #print str(Res).decode('utf-8')
                return Res
##            else:
##                time.sleep(20)
##                return getXML(sTime, eTime, stcd, tDivide)
        except:
            time.sleep(20)
            return getXML(sTime, eTime, stcd, tDivide)
    return getXML(sTime, eTime, stcd, tDivide)

def SaveXML2Csv(Res, findName, savePath, year):
    tree = xmlTree.fromstring(Res)
    nodes = tree.findall(findName)
    if not nodes:
        return 0
    else:
        f=open(savePath,"a")
##        titleline = ""
##        for Title in nodes[0]:
##            titleline += str(Title.tag.encode('utf-8'))+","
##        titleline+="\n"
##        f.write(titleline)
        for node in nodes:
            itemline = ""
            month = str(node[0].text.encode('utf-8'))[0:2]
            day = str(node[0].text.encode('utf-8'))[5:7]
            HH = str(node[0].text.encode('utf-8'))[10:12]
            itemline+=str(year)+"/"+month+"/"+day+" "+HH+":00"+","+str(node[1].text.encode('utf-8'))+"\n"
            #print itemline
##            if float(node[1].text)==0:
##                continue
##            else:
##                itemline+=str(year)+"-"+str(node[0].text.encode('utf-8'))+","+str(node[1].text.encode('utf-8'))+"\n"
##                print itemline
            f.write(itemline)
        f.close()
        return 1


if __name__ == '__main__':
    print "Beigin to download YcRainSum data!"

##    newSiteLines = []
##    for i in range(len(ZhanHao)):
##        xmlText = GetYcRainSum(ZhanHao[i], "2014-07-01 08:00", "2014-07-03 08:00", "1440")
##        #print str(xmlText).decode('utf-8')
##        savePath = r'E:\RainfallData_Anhui\YlZzt\%s.csv' % ZhanMing[i]
##        #print savePath
##        if SaveXML2Csv(xmlText, ".//YLZZT", savePath):
##            newSiteLine = ZhanHao[i]+","+ZhanMing[i]
##            newSiteLines.append(newSiteLine)
##            print i,newSiteLine
##    print len(newSiteLines)
##    f=open(r"e:\NewRainfallSites.txt","w")
##    for line in newSiteLines:
##        f.write(line)
##    f.close()

    f=open(r"E:\data\Dianbu\observed\precipitation_download\Sites_P_IDs_dianbu.txt","r")
    ZhanHaos = []
    for eachSite in f:
        ZhanHaos.append(eachSite.split('\n')[0])
    f.close()
    #print len(ZhanHaos)
    print ZhanHaos
    def downData(start, end, ZhanHao, year):
        xmlText = GetYcRainSum(start, end, ZhanHao, "60")
        savePath = r'E:\data\Dianbu\observed\precipitation_download\%s.txt' % ZhanHao
        success = SaveXML2Csv(xmlText, ".//GetRainValue", savePath, year)
        #print success
    #ZhanHaos = ['62903180','62942737','62942707','62915310','62933800','62942747','62922800','62942717','62942757']
    #years = ['2005','2006','2007','2008','2009','2010','2011','2012','2013','2014']
    years = ['2010','2011','2012','2013','2014','2015']
    #months = ['01','02','03','04','05','06','07','08','09','10','11','12']
    #downData('2013-12-01 00:00','2013-12-31 00:00', '62903180')

    for ZhanHao in ZhanHaos:
        for year in years:
            print "Downloading "+str(ZhanHao)+"'s data in "+str(year)+" ..."
            sTime = str(year)+'-01-01 00:00'
            eTime = str(year)+'-12-31 23:00'
            print ZhanHao,sTime,eTime
            downData(sTime,eTime, ZhanHao, year)
        print "Download "+str(ZhanHao)+"'s data successfully!"

    print "Download Succeed!"

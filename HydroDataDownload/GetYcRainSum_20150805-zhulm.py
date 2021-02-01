# coding=utf-8

import urllib2,httplib,string,sys,time
from xml.etree import ElementTree as xmlTree

#--------获取页面，保存为XML--------------------
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
            #-------------这个页面打不开----------
            conn = httplib.HTTP("yc.wswj.net")
            #-------------这个页面打不开----------
            # request是自动发送header，putrequest要手动发送header(两者之间的区别)
            conn.putrequest("POST","/ahyc/web_rain/Service.asmx")
            
            conn.putheader("Accept","*/*")
            conn.putheader("Accept-Encoding","gzip,deflate,sdch")
            conn.putheader("Accept-Language","zh-CN,zh;q=0.8,en;q=0.6")
            conn.putheader("Host","yc.wswj.net")
            conn.putheader("Origin","http://yc.wswj.net")
            #conn.putheader("Connection","keep-alive");
            #-------这个页面可以打开，是降水分布的网址--------这个页面含有降水数据，不知道如何查看页面具体内容--------------
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

        except:
            time.sleep(20)
            return getXML(sTime, eTime, stcd, tDivide)
    return getXML(sTime, eTime, stcd, tDivide)


#---------------将获取的XML站点转换为“CSV”格式-----------------
def SaveXML2Csv(Res, findName, savePath, year):
    tree = xmlTree.fromstring(Res)
    nodes = tree.findall(findName)
    if not nodes:
        return 0
    else:        
        f=open(savePath,"a")

        for node in nodes:
            itemline = ""
            month = str(node[0].text.encode('utf-8'))[0:2]
            day = str(node[0].text.encode('utf-8'))[5:7]
            HH = str(node[0].text.encode('utf-8'))[10:12]
            itemline+=str(year)+"/"+month+"/"+day+" "+HH+":00"+","+str(node[1].text.encode('utf-8'))+"\n"
            #print itemline

            f.write(itemline)
        f.close()
        return 1

#--------------主函数入口------------------------
if __name__ == '__main__':
    print "Beigin to download YcRainSum data!"

    
    f=open(r"D:\WorkSpace\Download_RainData\Zhanhao.txt","r")

    
    ZhanHaos = []
    for eachSite in f:   
        ZhanHaos.append(eachSite.split('\n')[0])
    f.close()
    #print len(ZhanHaos)
    print ZhanHaos
    
    def downData(start, end, ZhanHao, year):
        #------------开始下载页面-----------------
        xmlText = GetYcRainSum(start, end, ZhanHao, "60")
        savename=ZhanHao+ '-' +year

        
        savePath = r'D:\WorkSpace\Download_RainData\2011\%s.txt' % savename

        
        #------------调用前面函数，进行格式转换--------------
        success = SaveXML2Csv(xmlText, ".//GetRainValue", savePath, year)
    #ZhanHaos = ['62903180','62942737','62942707','62915310','62933800','62942747','62922800','62942717','62942757']
        
    #-----------降水数据从2007年开始才有记录--------------------
    #years = ['2007','2008','2009','2010','2011','2012','2013','2014','2015']
    years = ['2013']
    #years = ['2015']
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
            
            
    


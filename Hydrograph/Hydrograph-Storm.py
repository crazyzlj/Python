# coding=utf-8
#import pylab
import datetime,os,sys
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
import os, time

def PlotResult(tStart, tEnd, qFile, clr, tOffset=0):
    f = open(qFile)
    lines = f.readlines()
    f.close()
    
    tlist = []
    qlist = []
    for line in lines:
        items = line.split()
        date = datetime.datetime.strptime(items[0]+" "+items[1], '%Y-%m-%d %X')
        date = datetime.timedelta(minutes=tOffset) + date
        #print date
        if date < tStart or date > tEnd:
            continue
        tlist.append(date)
        qlist.append(float(items[2]))
    p, = plt.plot_date(tlist, qlist, clr,xdate=True, ydate=False, ls='-', marker='o', linewidth=2.0)
    return qlist, p

def PlotPrec(ax, precFile, tStart, tEnd, clr):
    f = open(precFile)
    lines = f.readlines()
    f.close()
    tlist = []
    qlist = []
    for line in lines:
        items = line.split()
        startDate = datetime.datetime.strptime(items[0]+" "+items[1], '%Y-%m-%d %X')
        endDate = datetime.datetime.strptime(items[0]+" "+items[2], '%Y-%m-%d %X')
        if startDate < tStart or endDate > tEnd:
            continue
        tlist.append(startDate)
        tlist.append(startDate)
        tlist.append(endDate)
        tlist.append(endDate)
        qlist.append(0)
        qlist.append(float(items[3]))
        qlist.append(float(items[3]))
        qlist.append(0)

    p, = ax.plot_date(tlist, qlist, clr,xdate=True, ydate=False)
    ax.fill(tlist,qlist,'b')
    return qlist, p
        
def NashCoef(qObs, qSimu):
    n = min(len(qObs), len(qSimu))
    ave = sum(qObs)/n
    a1 = 0
    a2 = 0
    for i in range(n):
        a1 = a1 + pow(qObs[i]-qSimu[i], 2)
        a2 = a2 + pow(qObs[i] - ave, 2)
    return 1 - a1/a2

def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
if __name__ == '__main__':
    year=1988
    tStart = datetime.datetime(year, 8, 7, 19)
    tEnd = datetime.datetime(year, 8, 8, 19)
    baseFolder = currentPath()
    
    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    #fig.autofmt_xdate() this code should be here, other than the end of this program!!!
    sim_qFile = baseFolder+r'\simuS.txt'
    obs_qFile = baseFolder+r'\obsS.txt'    
    tOffset = 0
    qSimu, pSimu = PlotResult(tStart, tEnd, sim_qFile, 'r', tOffset)  
    qObs, pObs = PlotResult(tStart, tEnd, obs_qFile, 'g', tOffset)
    fsize = 16
    plt.xlabel(u"Time",fontsize=fsize)
    plt.ylabel(u'Discharge(m3/s)',fontsize=fsize)
    
    plt.legend([pObs, pSimu], ["Observation", "Simulation"], loc=7)
    ns = NashCoef(qObs, qSimu)
    plt.title("Nash: %.3f" % (ns,))
    ax.set_ylim(min(min(qSimu),min(qObs))-10,1.4*max(max(qSimu),max(qObs)))
    
    ax2 = ax.twinx()
    ax2.set_ylabel(r"Precipitation (mm)", fontsize=fsize)
    precFile = baseFolder+r'\prec.txt'
    precList, precP = PlotPrec(ax2, precFile, tStart, tEnd, 'b')
    ax2.set_ylim(4*max(precList),0)

    hours = HourLocator(byhour=range(24),interval=2)
    hoursFmt = DateFormatter('%b,%d %Hh')
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(hoursFmt)
    ax.autoscale_view()
#    ax2.xaxis.set_major_locator(hours)
#    ax2.xaxis.set_major_formatter(hoursFmt)
#    ax2.autoscale_view()
    
    plt.grid(True)
    plt.show()
    
    print "Succeed!"

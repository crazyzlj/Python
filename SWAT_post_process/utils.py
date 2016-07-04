import os,sys

def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
def StripStr(str):
    ### @Function: Remove space(' ') and indent('\t') at the begin and end of the string
    oldStr = ''
    newStr = str
    while oldStr != newStr:
        oldStr = newStr
        newStr = oldStr.strip('\t')
        newStr = newStr.strip(' ')
    return newStr
def SplitStr(str, spliter=None):
    ### @Function: Split string by spliter space(' ') and indent('\t') as default
    spliters = [' ','\t']
    if spliter is not None:
        spliters.append(spliter)
    destStrs = []
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
            destStrs = []
        if oldDestStrs == srcStrs:
            destStrs = srcStrs[:]
            break
    return destStrs


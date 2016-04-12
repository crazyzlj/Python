### @Description: This program helps you to update SWAT database (.mdb) from the calibrated parameters from SWAT-CUP.
### @Reference: SWAT-CUP: SWAT Calibration and Uncertainty Programs - A User Manual. Eawag, 2015.
### @Usage: 1. Make sure you have python 2.x (x86) and pyodbc installed.
###         2. Put this script in the same folder with model.in and {your swat project name}.mdb.
###         3. Just specify your swat project name to SWAT_PROJ_NAME.
###         4. Run it.
###@version: 1.0-beta
###@DONE   : Update parameters in Access database
###@TODO   : Update parameters in the .dat files, e.g., plant.dat
###@author : Liang-Jun Zhu
###@Email  : zlj@lreis.ac.cn
###@website: zhulj.science

import pyodbc
from utils import *

ext2Table = {'mgt':'mgt1'}


class paraIdentifier:
    ### the parameter identifier format proposed by SWAT-CUP
    ### x__<parname>.<ext>__<hydrogrp>__<soltext>__<landuse>__<subbsn>__<slope>
    def __init__(self):
        self.name      = ''    ### SWAT parameter name as it appears in the Absolute_SWAT_Values.txt
        self.ext       = ''    ### SWAT file extention code or table name in SWAT database, e.g., sol, hru, rte, etc.
        self.hydrogrp  = []    ### (Optional) soil hydrological group ('A', 'B', 'C', or 'D')
        self.soltext   = []    ### (Optional) soil texture
        self.landuse   = []    ### (Optional) landuse
        self.subbsn    = []    ### (Optional) subbasin number(s)
        self.slope     = []    ### (Optional) slope, e.g., '0-20'
        self.indent    = ''    ### identifier code, v means replaced, a means added, r means multiplied.
        self.value     = 9999  ###
        self.lyr       = []    ### (Optional) soil layer number(s), e.g., 1,2,4-6 means 1,2,4,5,6
    def printStr(self):
        print "indentifer: %s, name: %s, table: %s, layers: %s, hydroGRP: %s, soil texture: %s, landuse: %s, subbasin: %s, slope: %s" % \
              (self.indent, self.name, self.ext, self.lyr, self.hydrogrp, self.soltext, self.landuse, self.subbsn, self.slope)

def ExtractMultiNums(str):
    ### the foundamental format of str is 1,2,4-6.
    orgNums = SplitStr(str, ',')
    destNums = []
    if len(orgNums) == 1:
        tempNumStrs = SplitStr(orgNums[0], '-')
        if len(tempNumStrs) == 1:
            return [int(tempNumStrs[0])]
        elif len(tempNumStrs) == 2:
            iStart = int(tempNumStrs[0])
            iEnd = int(tempNumStrs[1])
            for i in range(iStart, iEnd+1):
                destNums.append(i)
        else:
            print "Error occurred in %s in model.in!" % str
            sys.exit(1)
    else:
        for numStr in orgNums:
            try:
                i = int(numStr)
                destNums.append(i)
            except ValueError:
                tempNumStrs = SplitStr(numStr, '-')
                if len(tempNumStrs) == 2:
                    iStart = int(tempNumStrs[0])
                    iEnd = int(tempNumStrs[1])
                    for i in range(iStart, iEnd+1):
                        destNums.append(i)
                else:
                    print "Please check the format of %s!" % str
                    sys.exit(1)
    return destNums
def ReadModelIn(infile):
    f = open(infile)
    paraObjs = []
    for line in f:
        line = StripStr(line.split('\n')[0])
        if line != '' and line.find('//') < 0:
            tempParaStrs = SplitStr(line)
            # print tempParaStrs
            if len(tempParaStrs) != 2:
                print "Please check the item %s in model.in!" % tempParaStrs
                sys.exit(1)
            else:
                tempParaObj = paraIdentifier()
                tempParaObj.indent = tempParaStrs[0][0]
                tempParaObj.value = float(tempParaStrs[1])
                tempPrefixs = tempParaStrs[0].split('__')
                #print tempPrefixs
                if len(tempPrefixs) > 1:
                    #print  tempPrefixs[1]
                    tempName, tempExt = tempPrefixs[1].split('.')
                    if ext2Table.has_key(tempExt):
                        tempParaObj.ext = ext2Table.get(tempExt)
                    else:
                        tempParaObj.ext = tempExt
                    tempNameStrs = tempName.split('(')
                    if len(tempNameStrs) == 1:
                        tempParaObj.name = tempName
                    else:
                        tempParaObj.name = tempNameStrs[0]
                        tempLyrStrs = tempNameStrs[1].split(')')
                        if tempLyrStrs[0] != '':
                            tempParaObj.lyr = ExtractMultiNums(tempLyrStrs[0])
                        else:
                            ### all layers, -1 is indicator in the following process
                            tempParaObj.lyr = [-1]
                    if len(tempPrefixs) > 2 and tempPrefixs[2] != '':
                        tempParaObj.hydrogrp = SplitStr(tempPrefixs[2],',')
                    if len(tempPrefixs) > 3 and tempPrefixs[3] != '':
                        tempParaObj.soltext = SplitStr(tempPrefixs[3],',')
                    if len(tempPrefixs) > 4 and tempPrefixs[4] != '':
                        tempParaObj.landuse = SplitStr(tempPrefixs[4],',')
                    if len(tempPrefixs) > 5 and tempPrefixs[5] != '':
                        tempParaObj.subbsn = ExtractMultiNums(tempPrefixs[5])
                    if len(tempPrefixs) > 6 and tempPrefixs[6] != '':
                        tempParaObj.slope = SplitStr(tempPrefixs[6],',')
                else:
                    print "Please check the item %s in model.in!" % tempParaStrs[0]
                    sys.exit(1)
                paraObjs.append(tempParaObj)
    f.close()
    # for para in paraObjs:
    #     para.printStr()
    return paraObjs
def findFields(MDBPath, tableName, paraName):
    odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=;PWD=;' % MDBPath
    #print odbc_conn_str
    conn = pyodbc.connect(odbc_conn_str)
    cursor = conn.cursor()
    field_sel = []
    for row in cursor.columns(table=tableName):
        tempName = row.column_name
        if tempName.find(paraName) == 0:
            field_sel.append(tempName)
    return field_sel
def ConstructSQLs(paraObjs, absValues, MDBPath):
    SQLStrings = []
    for para in paraObjs:
        filterHydgrp = ""
        if para.hydrogrp != []:
            for hyd in para.hydrogrp:
                filterHydgrp += " HYDGRP='%s' or " % hyd
            filterHydgrp = filterHydgrp[:(len(filterHydgrp)-3)]
        filterSoltext = ""
        if para.soltext != []:
            for text in para.soltext:
                filterSoltext += " TEXTURE='%s' or " % text
            filterSoltext = filterSoltext[:(len(filterSoltext)-3)]
        filterLanduse = ""
        if para.landuse != []:
            for lu in para.landuse:
                filterLanduse += " LANDUSE='%s' or " % lu
            filterLanduse = filterLanduse[:(len(filterLanduse)-3)]
        filterSlope = ""
        if para.slope != []:
            for slp in para.slope:
                filterSlope += " SLOPE_CD='%s' or " % slp
            filterSlope = filterSlope[:(len(filterSlope)-3)]
        filterSubbsn = ""
        if para.subbsn != []:
            for bsn in para.subbsn:
                filterSubbsn += " SUBBASIN=%d or " % bsn
            filterSubbsn = filterSubbsn[:(len(filterSubbsn)-3)]
        filterStr = "WHERE "
        if filterHydgrp != "":
            filterStr += "(%s) and " % filterHydgrp
        if filterLanduse != "":
            filterStr += "(%s) and " % filterLanduse
        if filterSlope != "":
            filterStr += "(%s) and " % filterSlope
        if filterSoltext != "":
            filterStr += "(%s) and " % filterSoltext
        if filterSubbsn != "":
            filterStr += "(%s) and " % filterSubbsn
        paraNames = []
        if para.lyr != []:
            if para.lyr[0] == -1:
                paraNames = findFields(MDBPath, para.ext, para.name)
            else:
                for l in para.lyr:
                    paraNames.append(para.name+str(l))
        else:
            paraNames.append(para.name)
        #print paraNames
        curSQLStrs = []
        absValueSQLStrs = []
        for paraname in paraNames:
            if para.indent == 'v':
                baseSQLStr = "UPDATE %s SET %s = %f " % (para.ext, paraname, para.value)
            elif para.indent == 'a':
                baseSQLStr = "UPDATE %s SET %s = %s + %f " % (para.ext, paraname, paraname, para.value)
            elif para.indent == 'r':
                baseSQLStr = "UPDATE %s SET %s = %s * (1 + %f) " % (para.ext, paraname, paraname, para.value)
            else:
                print "Error occurred in Constructing SQL, please check %s in model.in" % paraname
                sys.exit(1)
            if absValues.has_key(para.name):
                MinMaxValues = absValues.get(para.name)
                absValueSQLStrs.append("UPDATE %s SET %s = %f WHERE %s < %f;" % (para.ext, paraname, MinMaxValues[0],paraname, MinMaxValues[0]))
                absValueSQLStrs.append("UPDATE %s SET %s = %f WHERE %s > %f;" % (para.ext, paraname, MinMaxValues[1],paraname, MinMaxValues[1]))
            curSQLStrs.append(baseSQLStr)
        #print curSQLStrs
        if filterStr != "WHERE ":
            filterStr = filterStr[:(len(filterStr)-4)]
        else:
            filterStr = ""
        for sql in curSQLStrs:
            sql += filterStr
            sql += ";"
            SQLStrings.append(sql)
        SQLStrings.extend(absValueSQLStrs)
    # for sql in SQLStrings:
    #     print sql
    return SQLStrings
def UpdateSWATDatabase(SWAT_MDB, SQLs):
    odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=;PWD=;' % SWAT_MDB
    #print odbc_conn_str
    conn = pyodbc.connect(odbc_conn_str)
    cursor = conn.cursor()
    for sql in SQLs:
        print "--Execute SQL: %s..." % sql
        cursor.execute(sql)
        print "---- {} rows updated!".format(cursor.rowcount)
    cursor.commit()
def ReadAbsoluteVal(txt):
    f = open(txt)
    absSWATVal = {}
    for line in f:
        line = StripStr(line.split('\n')[0])
        if line != '' and line.find('//') < 0:
            tempParaStrs = SplitStr(StripStr(line.split('\n')[0]))
            #print tempParaStrs[0:3]
            try:
                minV = float(tempParaStrs[1])
                maxV = float(tempParaStrs[2])
                absSWATVal[tempParaStrs[0]] = [minV, maxV]
            except ValueError:
                print "Extract Absolute SWAT values failed! \nPlease Check %s and retry!" % txt
                sys.exit(1)
    f.close()
    #print absSWATVal
    return absSWATVal
if __name__ == '__main__':
    PROJ_PATH = currentPath()
    SWAT_PROJ_NAME = 'zts2'
    SWAT_MDB = PROJ_PATH + os.sep + SWAT_PROJ_NAME + ".mdb"
    MODEL_IN = PROJ_PATH + os.sep + "model.in"
    ABS_SWAT_VAL_TXT = PROJ_PATH + os.sep + "Absolute_SWAT_Values.txt"

    #SWAT_MDB = r'E:\test\zts2.mdb'
    #MODEL_IN = r'E:\test\model.in'
    #ABS_SWAT_VAL_TXT = r'E:\test\Absolute_SWAT_Values.txt'

    PARA_OBJs = ReadModelIn(MODEL_IN)
    ABS_SWAT_VAL = ReadAbsoluteVal(ABS_SWAT_VAL_TXT)
    SQLs = ConstructSQLs(PARA_OBJs, ABS_SWAT_VAL, SWAT_MDB)
    UpdateSWATDatabase(SWAT_MDB, SQLs)


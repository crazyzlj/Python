import pyodbc
import sys,os
def readTable(mdbfile, tableName, findField, findValue, csvfile):
    odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=;PWD=;' % mdbfile
    #print odbc_conn_str
    conn = pyodbc.connect(odbc_conn_str)
    cursor = conn.cursor()
    field_sel = ["YEAR","MON","FLOW_OUTcms","SED_OUTtons","NO3_OUTkg","NH4_OUTkg","NO2_OUTkg","TOT_Nkg","TOT_Pkg","MINP_OUTkg","ORGP_OUTkg"]
    field_sel_idx = []
    fields = []
    fields_str = ''
    for row in cursor.columns(table=tableName):
        fields.append(row.column_name)
    for field in field_sel:
        if field in fields:
            field_sel_idx.append(fields.index(field))
            fields_str += field
            fields_str += ','
    #print fields_str
    query = "SELECT * FROM %s WHERE %s=%s" % (tableName, findField, findValue)
    #print query
    cursor.execute(query)
    rows = cursor.fetchall()
    f = open(csv_file,'w')
    f.write(fields_str)
    f.write('\n')
    for row in rows:
        row_str = ''
        for i in field_sel_idx:
            row_str += str(row[i])
            row_str += ","
        #print row
        #print row_str
        f.write(row_str)
        f.write('\n')
    f.close()

def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

if __name__ == '__main__':
    path = currentPath()
    #SWAT_output_mdb_file = r'E:\data_m\QSWAT_projects\ZhongTianShe2\zts2\Scenarios\sim8\TablesOut\SWATOutput.mdb'
    #csv_file = r'E:\data_m\QSWAT_projects\ZhongTianShe2\zts2\Scenarios\sim8\TablesOut\rch.csv'
    SWAT_output_mdb_file = path + os.sep + "SWATOutput.mdb"
    # csv_file = path + os.sep + "rch.csv"
    # readTable(SWAT_output_mdb_file, "rch", "SUB", 11, csv_file)
    ## the following code can export all reaches
    subbsnNum = 15
    for i in range(1, subbsnNum+1):
        csv_file = path + os.sep + "rch%s.csv" % str(i)
        readTable(SWAT_output_mdb_file, "rch", "SUB", i, csv_file)
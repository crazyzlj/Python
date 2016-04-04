import pyodbc
import sys,os
import numpy
def statsOutput(mdbfile, tableName, findField, findValue, years, fieldSel, csvfile):
    odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=;PWD=;' % mdbfile
    #print odbc_conn_str
    conn = pyodbc.connect(odbc_conn_str)
    cursor = conn.cursor()
    field_sel_idx = []
    fields = []
    fields_str = ''
    for row in cursor.columns(table=tableName):
        fields.append(row.column_name)
    for field in fieldSel:
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

    SWAT_output_mdb_file = r'E:\data_m\QSWAT_projects\Done\baseSim_unCali\baseSim_unCali\Scenarios\Default\TablesOut\SWATOutput.mdb'
    csv_file = r'E:\data_m\QSWAT_projects\Done\baseSim_unCali\baseSim_unCali\Scenarios\Default\TablesOut\rch_stats.csv'
    #path = currentPath()
    #SWAT_output_mdb_file = path + os.sep + "SWATOutput.mdb"
    #csv_file = path + os.sep + "rch_stats.csv"

    field_sel = ["FLOW_OUTcms","SED_OUTtons","NO3_OUTkg","NH4_OUTkg","NO2_OUTkg","TOT_Nkg","TOT_Pkg","MINP_OUTkg","ORGP_OUTkg"]
    year_sel = [2014]
    subbsnNum = 15
    statsOutput(SWAT_output_mdb_file,'rch','SUB',subbsnNum,year_sel,field_sel,csv_file)




import csv

from dbfread import DBF

if __name__ == '__main__':
    dbff = r'C:\Users\ZhuLJ\Desktop\test\aug2.DBF'
    csvf = r'C:\Users\ZhuLJ\Desktop\test\aug2.csv'
    table = DBF(dbff)
    f = open(csvf, 'w')
    writerobj = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    header = [v.encode('utf-8') for v in table.field_names]
    writerobj.writerow(header)
    for record in table:
        currec = list()
        for v in record.values():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            elif v is None:
                v = ''
            else:
                v = str(v)
            if len(v) > 8 and (v[0:2] == '14' or v[0:2] == '13' or v[0:2] == '622'):
                v = '\'%s' % v
            currec.append(v)
        writerobj.writerow(currec)
    f.close()

import sys,os,arcpy
##os.chdir(r'd:/test')
##try:
##    datFile = open("2001_2010_tmn.dat","r")
##except IOError:
##    print sys.stderr, "File could not be opened"
##count = 0
##FileNo = 360
##os.system('cd. > temp.dat')
##curFile = open("temp.dat","w")
##for line in datFile:
##    count = count+1
##    if count%360 == 0:
##        FileNo = FileNo+1
##        curFile.write(line)
##        curFile.close()
##        os.system('rename d:\\test\\temp.dat '+str(FileNo)+'.dat')
##        print str(FileNo)+".dat has been succeed!"
##        os.system('cd. > temp.dat')
##        curFile = open("temp.dat","w")  
##    else:
##        curFile.write(line)
##print count,FileNo
##datFile.close()
##The single dat file has been separated into 1308 files.
##Then, we will inverse the rows of each dat file.
##And rename it to the corresponding ascii file.
##So, we can use ArcGIS's ArcPy to convert ascii files to GRID.

from arcpy import env
env.workspace = r'd:\test'
os.chdir(r'd:\test')
##for i in range(1971,2010):
##    cmd = 'mkdir "'+str(i)+'"\\'
##    os.system(cmd)
arcpy.gp.overwriteOutput = 1
##for datfile in os.listdir("."):
##    if os.path.isfile(datfile) and (os.path.splitext(datfile)[1][1:].lower()=='dat'):
##        print datfile
##        os.system('cd. > temp.asc')
##        curDatFile = open(datfile,"r")
##        curAscFile = open("temp.asc","w")
##        curAscFile.write("NCOLS 720\n")
##        curAscFile.write("NROWS 360\n")
##        curAscFile.write("XLLCORNER -180\n")
##        curAscFile.write("YLLCORNER -90\n")
##        curAscFile.write("CELLSIZE 0.5\n")
##        curAscFile.write("NODATA_VALUE -999\n")
##        records = curDatFile.readlines()
##        ##print len(records)
##        for i in range(len(records),0,-1):
##            curAscFile.write(records[i-1])
##        curAscFile.close()
##        curDatFile.close()
##        os.system('rename d:\\test\\temp.asc '+str(os.path.splitext(datfile)[0])+'.asc')
for ascfile in os.listdir("."):
    ##print ascfile,os.path.splitext(ascfile)[1][1:].lower(),os.path.isfile(ascfile)
    if (os.path.splitext(ascfile)[1][1:].lower()=='asc'):
        ascfileName = str(os.path.splitext(ascfile)[0])
        ##print ascfileName
        if  int(ascfileName)%12 == 0:
            GridName = str(1970+int(ascfileName)/12)+str(12)
            GridFolder = str(1970+int(ascfileName)/12)
        elif int(ascfileName)%12 < 10:
            GridName = str(1971+int(ascfileName)/12)+str(0)+str(int(ascfileName)%12)
            GridFolder = str(1971+int(ascfileName)/12)
        else:
            GridName = str(1971+int(ascfileName)/12)+str(int(ascfileName)%12)
            GridFolder = str(1971+int(ascfileName)/12)
        print GridFolder,GridName
        arcpy.ASCIIToRaster_conversion("d:/test/"+ascfile,"d:/test/"+GridFolder+"/"+GridName,"INTEGER")
        prjfile = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        arcpy.DefineProjection_management("d:/test/"+GridFolder+"/"+GridName, prjfile)
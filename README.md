Author: Liangjun Zhu
Email: crazyzlj@gmail.com

If this repository occurs to you, it is truely my pleasure. And, I hope any of this code could make a help for you.
At fact, this repository is a collection of my study on python, especially based on Arcpy(ArcGIS 9.3.x ~ 10.x). Every single .py file or folder can work independently. 
Next, I will try my best to make a clear instrument for each function.

1. MultiValue2Zones
   This script will statistic the value of given rasters within the
zones of another polygon shapefile and report the results to a
CSV file.
This script can calculate values included "MEAN","MAJORITY",
"MAXIMUM","MEDIAN","MINIMUM","MINORITY","RANGE","STD","SUM",
"VARIETY". Each raster's value will be appended to the origin
shapefile's attribute table and named by the corresponding
raster's name.

2. AddNearAtrributesDirections
   This script is used to identify the surrounding polygon and add an attribute to save the relative direction, respectively.
   For detail of instrument and usage, please go to http://bbs.esrichina-bj.cn/ESRI/viewthread.php?tid=126293&extra=&page=1 , 
   http://bbs.esrichina-bj.cn/ESRI/viewthread.php?tid=60835&extra=&page=1  and http://bbs.esrichina-bj.cn/ESRI/viewthread.php?tid=85765.
   
3. CSV2PtsShp
   This is a very simple but useful script. To convert .CSV points coordinates to ESRI shapefile.
4. 

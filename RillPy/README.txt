RillPy is a tool for rill extraction and rill morphological characteristics calculation based on Arcpy,gdal,Scipy etc.

The whole tool contains of several modules:
   --Util.py          Some fundamental functions.
   --Subbasin.py      Subbasin delineation functions.
   --Hillslope.py     Hillslope delineation functions.
   --Rill.py          
   --ShoulderLine.py  
   --main.py          Configure the whole tool and make the entrance.
Functions in detail as follows.
   --Util
       ---currentPath()
	   ---makeResultFolder(rootdir)
	   ---downstream_index(DIR_VALUE, i, j)
	   ---ReadRaster(rasterFile)
	   ---WriteAscFile(filename, data, xsize, ysize, geotransform, noDataValue)
	   ---WriteGTiffFile(filename, nRows, nCols, data, geotransform, srs, noDataValue, gdalType)
	   ---WriteGTiffFileByMask(filename, data, mask, gdalType)
	   ---NashCoef(qObs, qSimu)
	   ---RMSE(list1, list2)
	   ---StdEv(list1)
	   ---UtilHydroFiles(DEMsrc, PreprocessDir)
	   ---RemoveLessPts(RasterFile,num,OutputRaster)
	   
   --Subbasin
       ---GenerateStreamNetByTHR(DEMbuf,FlowDirFile,FlowAccFile,threshold,folder)
	   ---GenerateWatershedByStream
	   ---RillIndexCalc(DEMbuf,StreamOrder)
	   ---
   --Hillslope
       ---isFirstStreamCell(StreamRaster, nodata, row, col, flow_dir)
	   ---isStreamSegmentCell(StreamRaster, nodata, row, col, flow_dir)
	   ---GetRillStartIdx(StreamLinks,nodata,FlowDir)
	   ---fillUpstreamCells(flow_dir,stream,nodata,hillslp,value,row,col)
	   ---DelineateHillslopes(StreamFile,FlowDirFile,HillslpFile)
	   ---
   --Rill
       ---IdentifyRillRidges(HillslpFile,StreamFile,FlowDirFile,FlowAccFile,WatershedFile,DEMfil,folder)
	   ---
In the main.py, there are several parameters:
   --DEMsrc       DEM source in which rill erosion occurs.
   --rootdir      The result folder. If the folder is not exists, it will be make; if rootdir 
                  is "", the result folder will in the current folder and named "RillPyResults"
				  In the rootdir, four folders will be created.
				  0Temp, 1Preprocess, 2Rill, 3Stats
   --streamTHR    Threshold for initial streamlinks and subbasions extraction.
                  If streamTHR = 0, the program will set the threshold as 1% percent of
				  accumulation by default; if 0< streamTHR < 1, it will be streamTHR*accum;
				  else if streamTHR > 1, it is the threshold.
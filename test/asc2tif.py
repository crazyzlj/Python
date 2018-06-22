from pygeoc.raster import RasterUtilClass

ascfile = r'C:\z_code\DTA\RasterClass\data\luid.asc'
tiffile = r'C:\z_code\DTA\RasterClass\data\luid.tif'

RasterUtilClass.raster_to_gtiff(ascfile, tiffile)
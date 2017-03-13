import matplotlib.pyplot as plt
import numpy as np
import netcdf4_pydap

credentials={'username': 'zhuliangjun',
             'password': 'Liangjun0130',
             'authentication_url': 'https://urs.earthdata.nasa.gov/'}
url = ('http://disc2.gesdisc.eosdis.nasa.gov/data//TRMM_L3/'
       'TRMM_3B42_Daily.7/2016/10/3B42_Daily.20161019.7.nc4')

with netcdf4_pydap.Dataset(url, **credentials) as dataset:
    data = dataset.variables['SLP'][0,:,:]
    plt.contourf(np.squeeze(data))
    plt.show()
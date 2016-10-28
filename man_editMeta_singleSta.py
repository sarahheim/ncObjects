import os, time
from netCDF4 import Dataset

ncPath = './SASS_SM-old/'
filesArr = os.listdir(ncPath)
filesArr.sort()
for fn in filesArr:
    ncName = os.path.join(ncPath, fn)
    print fn, os.path.isfile(ncName)
    if os.path.isfile(ncName):
        ncfile = Dataset(ncName, 'a', format='NETCDF4')
        #print ncfile.__dict__
        newMeta = {'creator_name': 'Institute of the Environment at University of California, Los Angeles'}
        ncfile.setncatts(newMeta)
        ncfile.setncatts({
        "date_modified": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), #time.ctime(time.time()),
        "date_issued": time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()), #time.ctime(time.time()),
        })
        ncfile.close()
        print 'EDITED'


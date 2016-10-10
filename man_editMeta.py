import os, time
from netCDF4 import Dataset

staMeta = {
'stearns_wharf' : {'abbr': 'UCSB'},
'newport_pier' : {'abbr': 'UCI'},
'santa_monica_pier' : {'abbr': 'UCLA'},
'scripps_pier' : {'abbr': 'UCSD'}
}

print staMeta
for i in range(13,17):
    for sta in staMeta:
       fn = sta+'-20'+str(i)+'.nc'
       print fn
       print staMeta[sta]['abbr']
       ncName = os.path.join('./SASS_copy/', fn)
       print os.path.isfile(ncName)
       if os.path.isfile(ncName):
           ncfile = Dataset(ncName, 'a', format='NETCDF4')
           #print ncfile.__dict__
           newMeta = {'contributor_name': staMeta[sta]['abbr']+'/SCCOOS, SCCOOS/IOOS/NOAA, SCCOOS'}
           ncfile.setncatts(newMeta)
           ncfile.setncatts({
           "date_modified": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), #time.ctime(time.time()),
           "date_issued": time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()), #time.ctime(time.time()),
           })
           print 'EDITED'


import os, time, uuid
from netCDF4 import Dataset

for i in range(15, 18):
    fn = 'CAF-20'+str(i).zfill(2)+'.nc'
    print fn
    ncName = os.path.join('./netcdf/', fn)
    if os.path.isfile(ncName):
        ncfile = Dataset(ncName, 'a', format='NETCDF4')
        # histPre = ncfile.getncattr('history').split(': ')[1]
        # #    print '\thistPre', histPre
        # histAdj = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(histPre))
        # print '\tnew "history" date:', histAdj
        # dtCrPre = ncfile.getncattr('date_modified')
        # #    print '\tdtCrPre', dtCrPre
        # dtCrAdj = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(dtCrPre))
        # print '\tnew "date_modified"', dtCrAdj

        # print ncfile.__dict__

        #global attr
        newMeta = {
            "geospatial_vertical_min": 0.9,
            "geospatial_vertical_max": 0.9
        }
        ncfile.setncatts(newMeta)

        # #variable attributes
        # print '\tpre-Standard_name:',ncfile.variables['pCO2_atm'].getncattr('standard_name')
        # ncfile.variables['pCO2_atm'].setncatts(              { 'standard_name': 'surface_partial_pressure_of_carbon_dioxide_in_sea_water' })
        # ncfile.variables['pCO2_atm_flagPrimary'].setncatts(  { 'standard_name': 'surface_partial_pressure_of_carbon_dioxide_in_sea_water' })
        # ncfile.variables['pCO2_atm_flagSecondary'].setncatts({ 'standard_name': 'surface_partial_pressure_of_carbon_dioxide_in_sea_water' })

        #depth variable attribute and value
        ncfile.variables['depth'].setncatts({
            'valid_min': 0.9,
            'valid_max': 0.9
        })
        ncfile.variables['depth'][0] = 0.9
        # ncfile.variables['depth'][0] = self.staMeta['depth']!!!

        #global attr, always update with any modification
        nowStr = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        ncfile.setncatts({
            "uuid": str(uuid.uuid4()),
            "date_modified": nowStr,
            "date_issued": nowStr
        })
        print '\tEDITED'

        ncfile.close()
    else:
        print "\tDid NOT find:", ncName

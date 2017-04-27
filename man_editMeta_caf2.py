import os, time, uuid
from netCDF4 import Dataset

for i in range(15, 18):
    fn = 'CAF-20'+str(i).zfill(2)+'.nc'
    print fn
    ncName = os.path.join('./netcdf/', fn)
    if os.path.isfile(ncName):
        ncfile = Dataset(ncName, 'a', format='NETCDF4')
        # print ncfile.__dict__

        #GLOBAL ATTRIBUTES
        newMeta = {
            'time_coverage_resolution': 'P1S'
        }
        ncfile.setncatts(newMeta)

        # #VARIABLE ATTRIBUTES
        # print '\tpre-Standard_name:',ncfile.variables['pCO2_atm'].getncattr('standard_name')
        # ncfile.variables['pCO2_atm'].setncatts(              { 'standard_name': 'surface_partial_pressure_of_carbon_dioxide_in_sea_water' })
        # ncfile.variables['pCO2_atm_flagPrimary'].setncatts(  { 'standard_name': 'surface_partial_pressure_of_carbon_dioxide_in_sea_water status_flag' })
        # ncfile.variables['pCO2_atm_flagSecondary'].setncatts({ 'standard_name': 'surface_partial_pressure_of_carbon_dioxide_in_sea_water status_flag' })
        # ncfile.variables['pCO2_atm_flagSecondary'].setncatts({ 'long_name': "Burkolator" })
        # ncfile.variables['temperature'].setncatts({ 'instrument':'instrument2' })
        # ncfile.variables['salinity'].setncatts({ 'instrument':'instrument2' })
        ncfile.variables['instrument1'].setncatts({
            'long_name': "Burkolator",
            'comment':"Burkolator",
            'make':"LI-COR",
            'model':"LI-840"
        })

        # instrument2 = ncfile.createVariable('instrument2', 'i') #Licor??
        # instrument2.setncatts({
        #     'long_name': "DirectLine DL423 Sensor Module",
        #     # 'comment':"DirectLine DL423 Sensor Module",
        #     'make':"Honeywell",
        #     'model':"DL423"
        # })
        #
        # crs = ncfile.createVariable('crs', 'd')
        # crs.grid_mapping_name = "latitude_longitude";
        # crs.longitude_of_prime_meridian = 0.0;
        # crs.epsg_code = "EPSG:4326" ;
        # crs.semi_major_axis = 6378137.0 ;
        # crs.inverse_flattening = 298.257223563 ;

        #global attr, always update with any modification
        nowStr = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        ncfile.setncatts({
            "uuid": str(uuid.uuid4()),
            "date_metadata_modified": nowStr,
            # "date_modified": nowStr,
            "date_issued": nowStr
        })
        print '\tEDITED'

        ncfile.close()
    else:
        print "\tDid NOT find:", ncName

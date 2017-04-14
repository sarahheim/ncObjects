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
            'Conventions':'CF-1.6, ACDD-1.3',
            'product_version': 'v1',
            'creator_type':'person',
            'creator_institution':'Scripps Institution of Oceanography (SIO)',
            'publisher_institution': 'Scripps Institution of Oceanography (SIO)',
            'publisher_type': 'position',
            'program': 'Southern California Coastal Ocean Observing System (SCCOOS)',
            'platform_vocabulary': 'GCMD Earth Science Keywords. Version 5.3.3',
            'platform': 'In Situ Land-based Platforms > Ocean Platform/Ocean Stations > Coastal Stations',
            'instrument_vocabulary': 'GCMD Earth Science Keywords. Version 5.3.3',
            'instrument': 'Earth Science > Oceans > Ocean Chemistry > Chlorophyll, Earth Science > Oceans > Ocean Optics > Turbidity, Earth Science > Oceans > Ocean Pressure > Water Pressure, Earth Science > Oceans > Ocean Temperature > Water Temperature, Earth Science > Oceans > Salinity/Density > Conductivity, Earth Science > Oceans > Salinity/Density > Salinity, Earth Science > Oceans > Water Quality, Earth Science>Oceans>Ocean Chemistry>pH, Earth Science>Oceans>Ocean Chemistry>Carbon Dioxide',
            'geospatial_bounds_crs': 'EPSG:4326',
            'geospatial_bounds_vertical_crs': 'EPSG:5829',
            'geospatial_bounds': 'POINT(-117.339 33.139)'
            "geospatial_vertical_units": 'm',
            'geospatial_vertical_positive': 'down',
        }
        ncfile.setncatts(newMeta)

        # #VARIABLE ATTRIBUTES
        # print '\tpre-Standard_name:',ncfile.variables['pCO2_atm'].getncattr('standard_name')
        # ncfile.variables['pCO2_atm'].setncatts(              { 'standard_name': 'surface_partial_pressure_of_carbon_dioxide_in_sea_water' })
        ncfile.variables['pCO2_atm_flagPrimary'].setncatts(  { 'standard_name': 'surface_partial_pressure_of_carbon_dioxide_in_sea_water status_flag' })
        ncfile.variables['pCO2_atm_flagSecondary'].setncatts({ 'standard_name': 'surface_partial_pressure_of_carbon_dioxide_in_sea_water status_flag' })
        ncfile.variables['pCO2_atm_flagSecondary'].setncatts({ 'long_name': "Burkolator" })
        ncfile.variables['temperature'].setncatts({ 'coverage_content_type':'physicalMeasurement' })
        ncfile.variables['salinity'].setncatts({ 'coverage_content_type':'physicalMeasurement' })
        ncfile.variables['pCO2_atm'].setncatts({ 'coverage_content_type':'physicalMeasurement' })
        ncfile.variables['TCO2_mol_kg'].setncatts({ 'coverage_content_type':'physicalMeasurement' })

        crs = ncfile.createVariable('crs', 'd')
        crs.grid_mapping_name = "latitude_longitude";
        crs.longitude_of_prime_meridian = 0.0;
        crs.epsg_code = "EPSG:4326" ;
        crs.semi_major_axis = 6378137.0 ;
        crs.inverse_flattening = 298.257223563 ;

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

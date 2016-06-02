#
# Author Sarah Heim
# Date create: May 2016
# Description: adjusting to class/objects, parts taken from sass.py
#
from abc import ABCMeta, abstractmethod
class NC(object):
    """
Class documentation: This root 'nc' class is an abstract class. 
It will be the base to make a netcdf file. 
Its children are 'cdip' and 'sccoos' (grandchildren 'sass' & 'caf')
    """
    __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self):
        #super(NC, self).__init__()
        print "init nc"
        self.dateformat = "%Y-%m-%dT%H:%M:%SZ"

    @abstractmethod
    def createNCshell(self, ncfile, sta):
        ##Meta
        ncfile.ncei_template_version = "NCEI_NetCDF_TimeSeries_Orthogonal_Template_v2.0"
        ncfile.featureType = "timeSeries"
        ncfile.Metadata_Conventions = 'Unidata Dataset Discovery v1.0'
        ncfile.Conventions = 'CF-1.6'
        ncfile.keywords = 'EARTH SCIENCE, OCEANS'
        ncfile.keywords_vocabulary = 'Global Change Master Directory (GCMD) Earth Science Keywords'
        ncfile.standard_name_vocabulary = 'CF Standard Name Table (v28, 07 January 2015)'
        ncfile.institution = 'Scripps Institution of Oceanography, University of California San Diego'
        ncfile.license = 'Data is preliminary and should not be used by anyone.'
        ncfile.geospatial_lon_units = 'degrees_east'
        ncfile.geospatial_lat_units = 'degrees_north'
        ncfile.time_coverage_units = 'seconds since 1970-01-01 00:00:00 UTC'
        ncfile.time_coverage_resolution = '1'

        lat = ncfile.createVariable('lat', 'f4')
        lat.standard_name = 'latitude'
        lat.long_name = 'latitude'
        lat.units = 'degrees_north'
        lat.axis = 'Y'
        ncfile.variables['lat'][0] = ips[ip]['lat']
        lon = ncfile.createVariable('lon', 'f4')
        lon.standard_name = 'longitude'
        lon.long_name = 'longitude'
        lon.units = 'degrees_east'
        lon.axis = 'X'
        ncfile.variables['lon'][0] = ips[ip]['lon']
        dep = ncfile.createVariable('depth', 'f4')
        dep.standard_name = 'depth'
        dep.long_name = 'depth'
        dep.units = 'm'
        dep.axis = 'Z'
        dep.positive = 'down'
        ncfile.variables['depth'][0] = ips[ip]['depth']
    
        return ncfile

    @abstractmethod
    def NCtimeMeta(ncfile):
        # SPECIFIC to file
        # Calculate. ISO 8601 Time duration
        times = ncfile.variables['time'][:]
        minTimeS = min(times)
        maxTimeS = max(times)
        minTimeT = time.gmtime(minTimeS)
        maxTimeT = time.gmtime(maxTimeS)
        ncfile.time_coverage_start = tupToISO(minTimeT)
        ncfile.time_coverage_end = tupToISO(maxTimeT)
        ncfile.time_coverage_duration = ISOduration(minTimeS, maxTimeS)
        ncfile.date_modified = time.ctime(time.time())
    
    #assumes there's a 'time' variable in data/ncfile
    @abstractmethod
    def dataToNC(ncName, subset, lookup):
    #    yr = str(yr)
    #    loc = ips[ip]['loc']
    #    ncName = os.path.join(ncpath, loc, loc + '-' + yr + '.nc')
    
        #print "dataToNC", os.path.dirname(ncName)
        if not os.path.isfile(ncName):
            ncfile = Dataset(ncName, 'w', format='NETCDF4')
            ncfile = createNCshell(ncfile, lookup)
            ncfile.variables['time'][:] = subset.index.astype('int64') // 10**9
            for attr in attrArr:
                #             ncfile.variables['temperature'][:] = subset['temperature'].values
                ncfile.variables[attr][:] = subset[attr].values
    
        else:
            ncfile = Dataset(ncName, 'a', format='NETCDF4')
            timeLen = len(ncfile.variables['time'][:])
            # length should be the same for time & all attributes
            ncfile.variables['time'][
                timeLen:] = subset.index.astype('int64') // 10**9
            for attr in attrArr:
                #atLen = len(ncfile.variables[attr][:])
                ncfile.variables[attr][timeLen:] = subset[attr].values
#        NCtimeMeta(ncfile) #commented out only for testing!!!
        ncfile.close()

class CDIP(NC):
    __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self):
        super(CDIP, self).__init__()
        print "init cdip"
        self.naming_authority = 'CDIP'

class SCCOOS(NC):
    __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self):
        super(SCCOOS, self).__init__()
        print "init sccoos"

        ##Meta
        self.naming_authority = 'sccoos.org'
        self.acknowledgment = 'The Southern California Coastal Ocean Observing System (SCCOOS) ' +\
            'is one of eleven regions that contribute to the national U.S. Integrated Ocean Observing System (IOOS).'
        self.publisher_name = 'Southern California Coastal Ocean Observing System'
        self.publisher_url = 'http://sccoos.org'
        self.publisher_email = 'info@sccoos.org'
        self.source = 'insitu observations'

class SASS(SCCOOS):
    def __init__(self):
        super(SASS, self).__init__()
        print "init sass"
        self.logsdir = r'/data/InSitu/SASS/data/'
        self.ncpath = '/data/InSitu/SASS/netcdfs/'
        self.fnformat = "%Y-%m/data-%Y%m%d.dat"

        self.staMeta = {'UCSB': {'loc': 'stearns_wharf',
                    'loc_name': 'Stearns Wharf',
                    'lat': 34.408,
                    'lon': -119.685,
                    'depth': '2',
                    'url': 'http://msi.ucsb.edu/',
                    'inst': 'Marine Science Institute at University of California, Santa Barbara'},
           'UCI': {'loc': 'newport_pier',
                   'loc_name': 'Newport Pier',
                   'lat': 33.6061,
                   'lon': -117.9311,
                   'depth': '2',
                   'url': 'http://uci.edu/',
                   'inst': 'University of California, Irvine'},
           'UCLA': {'loc': 'santa_monica_pier',
                    'loc_name': 'Santa Monica Pier',
                    'lat': 34.008,
                    'lon': -118.499,
                    'depth': '2',
                    'url': 'http://environment.ucla.edu/',
                    'inst': 'Institute of the Environment at the University of California, Los Angeles'},
           'UCSD': {'loc': 'scripps_pier',
                    'loc_name': 'Scripps Pier',
                    'lat': 32.867,
                    'lon': -117.257,
                    'depth': '5',
                    'url': 'https://sccoos.org/',
                    'inst': 'Southern California Coastal Ocean Observing System (SCCOOS) at Scripps Institution of Oceanography (SIO)'}}

        # IP Address of Shorestations
        self.ips = {'166.148.81.45': staMeta['UCSB'],
       '166.241.139.252': staMeta['UCI'],
       '166.241.175.135': staMeta['UCLA'],
       '132.239.117.226': staMeta['UCSD'],
       '172.16.117.233': staMeta['UCSD']}

        # header names to dat log files
        self.columns = ['server_date', 'ip', 'temperature', 'conductivity', 'pressure', 'aux1',
           'aux3', 'chlorophyll', 'aux4', 'salinity', 'dateDay', 'dateMon',
           'dateYr', 'time', 'sigmat', 'diagnosticVoltage', 'currentDraw']

        self.attrArr = ['temperature', 'conductivity', 'pressure', 'aux1', 'aux3', 'chlorophyll',  # NOT INCLUDING 'time'
           'conductivity_flagPrimary', 'conductivity_flagSecondary',
           'pressure_flagPrimary', 'pressure_flagSecondary',
           'salinity_flagPrimary', 'salinity_flagSecondary',
           'chlorophyll_flagPrimary', 'chlorophyll_flagSecondary']

    def createNCshell(self, ncfile, sta):
        #Move to NC class???
        flagPrim_flag_values = bytearray([1, 2, 3, 4, 9]) # 1UB, 2UB, 3UB, 4UB, 9UB ;
        flagPrim_flag_meanings = 'GOOD_DATA UNKNOWN SUSPECT BAD_DATA MISSING'
        flagSec_flag_values = bytearray([0, 1, 2, 3]) # 1UB, 2UB, 3UB, 4UB, 9UB ;
        flagSec_flag_meanings = 'UNSPECIFIED RANGE FLAT_LINE SPIKE'

        ##Meta
        ncfile.metadata_link = 'www.sccoos.org.progress/data-products/automateed-shore-stations/'
        ncfile.summary = 'Automated shore station with a suite of sensors that are ' +\
            'attached to piers along the nearshore California coast. ' + \
            'These automated sensors measure temperature, salinity, chlorophyll, turbidity ' + \
            'and water level at frequent intervals in the nearshore coastal ocean.' +\
            'This data can provide local and regional information on mixing and upwelling, ' +\
            'land run-off, and algal blooms.'
        ncfile.keywords = 'EARTH SCIENCE, OCEANS, SALINITY/DENSITY, SALINITY,  OCEAN CHEMISTRY,' +\
            ' CHLOROPHYLL, OCEAN TEMPERATURE, WATER TEMPERATURE, OCEAN PRESSURE, WATER PRESSURE'
        ncfile.project = 'Automated Shore Stations'
        ncfile.processing_level = 'QA/QC have been performed'
        ncfile.cdm_data_type = 'Station'
        ncfile.geospatial_lat_resolution = '2.77E-4'  # ?
        ncfile.geospatial_lon_resolution = '2.77E-4'  # ?
        ncfile.geospatial_vertical_units = 'm'  # ???
        ncfile.geospatial_vertical_resolution = '1'  # ???
        ncfile.geospatial_vertical_positive = 'down'  # ???

    # Create Dimensions
    # unlimited axis (can be appended to).
    time_dim = ncfile.createDimension('time', None)
    name_dim = ncfile.createDimension('name_strlen', size=25)

    #Create Variables
    time_var = ncfile.createVariable(
        'time', np.int32, ('time'), **kwargs)  # int64? Gives error
    # time_var.setncattr({'standard_name':'time', 'long_name': 'time', 'units':'seconds since 1970-01-01 00:00:00 UTC'})
    time_var.standard_name = 'time'
    time_var.units = 'seconds since 1970-01-01 00:00:00 UTC'
    time_var.long_name = 'time'
    time_var.calendar = 'julian' #use??
    time_var.axis = "T"
    temperature = ncfile.createVariable('temperature', 'f4', ('time'), **kwargs)
    temperature.standard_name = 'sea_water_temperature'
    temperature.long_name = 'sea water temperature'
    temperature.units = 'celsius'
    temperature.coordinates = 'time lat lon depth'
    temperature_flagPrim = ncfile.createVariable(
        'temperature_flagPrimary', 'B', ('time'), **kwargs)
    temperature_flagPrim.long_name = 'sea water temperature, qc primary flag'
    temperature_flagPrim.flag_values = flagPrim_flag_values
    temperature_flagPrim.flag_meanings = flagPrim_flag_meanings
    temperature_flagSec = ncfile.createVariable(
        'temperature_flagSecondary', 'B', ('time'), **kwargs)
    temperature_flagSec.long_name = 'sea water temperature, qc secondary flag'
    temperature_flagSec.flag_values = flagSec_flag_values
    temperature_flagSec.flag_meanings = flagSec_flag_meanings
    con = ncfile.createVariable('conductivity', 'f4', ('time'), **kwargs)
    con.standard_name = 'sea_water_electrical_conductivity'
    con.long_name = 'sea water electrical conductivity'
    con.units = 'S/m'
    con.coordinates = 'time lat lon depth'
    con_flagPrim = ncfile.createVariable(
        'conductivity_flagPrimary', 'B', ('time'), **kwargs)
    con_flagPrim.long_name = 'sea water electrical conductivity, qc primary flag'
    con_flagPrim.flag_values = flagPrim_flag_values
    con_flagPrim.flag_meanings = flagPrim_flag_meanings
    con_flagSec = ncfile.createVariable(
        'conductivity_flagSecondary', 'B', ('time'), **kwargs)
    con_flagSec.long_name = 'sea water electrical conductivity, qc secondary flag'
    con_flagSec.flag_values = flagSec_flag_values
    con_flagSec.flag_meanings = flagSec_flag_meanings
    pres = ncfile.createVariable('pressure', 'f4', ('time'), **kwargs)
    pres.standard_name = 'sea_water_pressure'
    pres.long_name = 'sea water pressure'
    pres.units = 'dbar'
    pres.coordinates = 'time lat lon depth'
    pres_flagPrim = ncfile.createVariable(
        'pressure_flagPrimary', 'B', ('time'), **kwargs)
    pres_flagPrim.long_name = 'sea water pressure, qc primary flag'
    pres_flagPrim.flag_values = flagPrim_flag_values
    pres_flagPrim.flag_meanings = flagPrim_flag_meanings
    pres_flagSec = ncfile.createVariable(
        'pressure_flagSecondary', 'B', ('time'), **kwargs)
    pres_flagSec.long_name = 'sea water pressure, qc secondary flag'
    pres_flagSec.flag_values = flagSec_flag_values
    pres_flagSec.flag_meanings = flagSec_flag_meanings
    a1 = ncfile.createVariable('aux1', 'f4', ('time'), **kwargs)
    a1.long_name = 'Auxiliary 1'  # Use Standard name for 1,3,4???
    a1.units = 'V'
    a1.coordinates = 'time lat lon depth'
    a3 = ncfile.createVariable('aux3', 'f4', ('time'), **kwargs)
    a3.long_name = 'Auxiliary 3'
    a3.units = 'V'
    a3.coordinates = 'time lat lon depth'
    chl = ncfile.createVariable('chlorophyll', 'f4', ('time'), **kwargs)
    chl.standard_name = 'mass_concentration_of_chlorophyll_a_in_sea_water'
    chl.long_name = 'sea water chlorophyll'
    chl.units = 'ug/L'  # which CF name??
    chl.coordinates = 'time lat lon depth'
    chl_flagPrim = ncfile.createVariable(
        'chlorophyll_flagPrimary', 'B', ('time'), **kwargs)
    chl_flagPrim.long_name = 'sea water chlorophyll, qc primary flag'
    chl_flagPrim.flag_values = flagPrim_flag_values
    chl_flagPrim.flag_meanings = flagPrim_flag_meanings
    chl_flagSec = ncfile.createVariable(
        'chlorophyll_flagSecondary', 'B', ('time'), **kwargs)
    chl_flagSec.long_name = 'sea water chlorophyll, qc secondary flag'
    chl_flagSec.flag_values = flagSec_flag_values
    chl_flagSec.flag_meanings = flagSec_flag_meanings
    a4 = ncfile.createVariable('aux4', 'f4', ('time'), **kwargs)
    a4.long_name = 'Auxiliary 4'
    a4.units = 'V'
    a4.coordinates = 'time lat lon depth'
    sal = ncfile.createVariable('salinity', 'f4', ('time'), **kwargs)
    sal.standard_name = 'sea_water_salinity'
    sal.long_name = 'sea water salinity'
    sal.units = '1e-3'
    sal.coordinates = 'time lat lon depth'
    sal_flagPrim = ncfile.createVariable(
        'salinity_flagPrimary', 'B', ('time'), **kwargs)
    sal_flagPrim.long_name = 'sea water salinity, qc primary flag'
    sal_flagPrim.flag_values = flagPrim_flag_values
    sal_flagPrim.flag_meanings = flagPrim_flag_meanings
    sal_flagSec = ncfile.createVariable(
        'salinity_flagSecondary', 'B', ('time'), **kwargs)
    sal_flagSec.long_name = 'sea water salinity, qc secondary flag'
    sal_flagSec.flag_values = flagSec_flag_values
    sal_flagSec.flag_meanings = flagSec_flag_meanings
    sig = ncfile.createVariable('sigmat', 'f4', ('time'), **kwargs)
    sig.standard_name = 'sea_water_density'
    sig.long_name = 'sea water density'
    sig.units = 'kg/m^3'
    sig.coordinates = 'time lat lon depth'
    dV = ncfile.createVariable('diagnosticVoltage', 'f4', ('time'), **kwargs)
    dV.long_name = 'diagnostic voltage'  # NO standard name???
    dV.units = 'V'
    dV.coordinates = 'time lat lon depth'
    cDr = ncfile.createVariable('currentDraw', 'f4', ('time'), **kwargs)
    cDr.long_name = 'current draw'  # NO standard name???
    cDr.units = 'mA'
    cDr.coordinates = 'time lat lon depth'

    nm = ncfile.createVariable('station', 'S1', 'name_strlen')
    nm.long_name = 'station_name'
    nm.cf_role = 'timeseries_id'
    ncfile.variables['station'][:len(ips[ip]['loc'])] = list(ips[ip]['loc'])

        return ncfile

class CAF(SCCOOS):
    def __init__(self):
        super(CAF, self).__init__()
        print "init caf"
        self.logsdir = r'/data/InSitu/Burkolator/data/CarlsbadAquafarm/CAF_Latest/'
        self.ncpath = '/data/InSitu/SASS/Burkolator/netcdf'
#        self.fnformat = "CAF_RTproc_%Y%m%d.dat" #!!!

    def createNCshell(self, ncfile):
        ##Meta
        ncfile.keywords = 'EARTH SCIENCE, OCEANS, SALINITY/DENSITY, SALINITY,  OCEAN CHEMISTRY,'##!!!
        ncfile.processing_level = 'QA/QC has not been performed' ##!!!
        ncfile.ip = "132.239.92.62"
        ncfile.metadata_link = 'www.sccoos.org.progress/data-products/'
        ncfile.summary = '' ##!!!
        ncfile.project = 'Carlsbad Auqafarm'
        ncfile.processing_level = 'QA/QC has not been performed'
        ncfile.cdm_data_type = 'Station'
        return ncfile


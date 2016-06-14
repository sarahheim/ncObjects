#
# Author Sarah Heim
# Date create: May 2016
# Description: adjusting to class/objects, parts taken from sass.py
#
import os, time, datetime, subprocess
import sassqc
import pandas as pd
import numpy as np
from netCDF4 import Dataset
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
        #print "init nc"
        self.dateformat = "%Y-%m-%dT%H:%M:%SZ"

    @abstractmethod
    def createNCshell(self, ncfile):
        pass

    @abstractmethod
    def text2nc(self, filename, lastRecorded=None):
        pass

    @abstractmethod
    # Loop through ALL log files and put in NC files
    def text2nc_all(self):
        pass

    # Append only the latest data since last writing to NC files
    @abstractmethod
    def text2nc_append(self):
        pass

    def addNCshell_NC(self, ncfile):
        print "addNCshell_NC"
        ##base metadata, can be overwritten
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
#        ncfile.variables['lat'][0] = ips[ip]['lat']
        lon = ncfile.createVariable('lon', 'f4')
        lon.standard_name = 'longitude'
        lon.long_name = 'longitude'
        lon.units = 'degrees_east'
        lon.axis = 'X'
#        ncfile.variables['lon'][0] = ips[ip]['lon']
        dep = ncfile.createVariable('depth', 'f4')
        dep.standard_name = 'depth'
        dep.long_name = 'depth'
        dep.units = 'm'
        dep.axis = 'Z'
        dep.positive = 'down'
#        ncfile.variables['depth'][0] = ips[ip]['depth']
    
        return ncfile



    def tupToISO(self, timeTup):
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', timeTup)
    
    # Only return Day, Hour, Min, Sec in ISO 8601 duration format
    # Designed, testing NSDate int, may work with epoch (subsec???)
    
    
    def ISOduration(self, minTimeS, maxTimeS):
        secDif = maxTimeS - minTimeS
        days = secDif / (3600 * 24)
        dayRem = secDif % (3600 * 24)
        hrs = dayRem / 3600
        hrRem = dayRem % 3600
        mins = hrRem / 60
        secs = hrRem % 60
        durStr = "P" + str(days) + "DT" + str(hrs) + "H" + \
            str(mins) + "M" + str(secs) + "S"
    #     print secDif, days, dayRem, hrs, hrRem, mins, secs, durStr
        return durStr

    def NCtimeMeta(self, ncfile):
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

    #filesize checker/resizer as a NC method
    def fileSizeChecker(self, ncfilepath):
        nameOnly = ncfilepath.split('/')[-1]
        if os.path.isfile(ncfilepath):
            fileMb = int(os.path.getsize(ncfilepath) / 1000000)
            if fileMb > 10:
#                tmpfilepath = '/tmp/' + ncfilename
#                temp = '/usr/local/bin/nccopy'
                temp = '/home/scheim/NCobj/nccopy'
                tmpfilepath = os.path.join(temp, nameOnly)
                origSz = os.path.getsize(ncfilepath)
                subprocess.call(['nccopy', ncfilepath, tmpfilepath])
                subprocess.call(['mv', tmpfilepath, ncfilepath])
                print 'RESIZED FILE: prev:', origSz, os.path.getsize(ncfilepath)

    
    #assumes there's a 'time' variable in data/ncfile
    def dataToNC(self, ncName, subset, lookup):
    #def dataToNC(yr, ip, subset): ##prev
    #    yr = str(yr)
    #    loc = ips[ip]['loc']
    #    ncName = os.path.join(ncpath, loc, loc + '-' + yr + '.nc')
    
        #print "dataToNC", os.path.dirname(ncName)
        if not os.path.isfile(ncName):
            ncfile = Dataset(ncName, 'w', format='NETCDF4')
            ncfile = self.createNCshell(ncfile, lookup)
            ncfile.variables['time'][:] = subset.index.astype('int64') // 10**9
            for attr in self.attrArr:
                #             ncfile.variables['temperature'][:] = subset['temperature'].values
                ncfile.variables[attr][:] = subset[attr].values
    
        else:
            ncfile = Dataset(ncName, 'a', format='NETCDF4')
            timeLen = len(ncfile.variables['time'][:])
            # length should be the same for time & all attributes
            ncfile.variables['time'][
                timeLen:] = subset.index.astype('int64') // 10**9
            for attr in self.attrArr:
                #atLen = len(ncfile.variables[attr][:])
                ncfile.variables[attr][timeLen:] = subset[attr].values
#        NCtimeMeta(ncfile) #commented out only for testing!!!
        ncfile.close()

class CDIP(NC):
    __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self):
        super(CDIP, self).__init__()
        #print "init cdip"

    def createNCshell(self, ncfile, sta):
        ncfile.naming_authority = 'CDIP'

class SCCOOS(NC):
    __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self):
        super(SCCOOS, self).__init__()
        #print "init sccoos"

    def addNCshell_SCCOOS(self, ncfile):
        self.addNCshell_NC(ncfile)
        print "addNCshell_SCCOOS"
        ##Meta
        ncfile.naming_authority = 'sccoos.org'
        ncfile.acknowledgment = 'The Southern California Coastal Ocean Observing System (SCCOOS)'
        ncfile.publisher_name = 'Southern California Coastal Ocean Observing System'
        ncfile.publisher_url = 'http://sccoos.org'
        ncfile.publisher_email = 'info@sccoos.org'
        ncfile.source = 'insitu observations'

    def getLastDateNC(self, ncFilename):
        if os.path.isfile(ncFilename):
            # open a the netCDF file for reading.
            ncfile = Dataset(ncFilename,'r')
            # read the last unix timestamp in variable named 'time'.
            unixtime = ncfile.variables['time'][-1:]
            # close the NetCDF file
            ncfile.close()
        else:
            unixtime = [1356998400] # 2013-01-01 00:00:00 UTC
        return pd.to_datetime(unixtime, unit='s', utc=None)[0].isoformat()

class SASS(SCCOOS):
    def __init__(self):
        super(SASS, self).__init__()
        #print "init sass"
        self.logsdir = r'/data/InSitu/SASS/data/'
#        self.ncpath = '/data/InSitu/SASS/netcdfs/'
        self.ncpath = '/home/scheim/NCobj'
        self.fnformat = "%Y-%m/data-%Y%m%d.dat"

#        self.columns = ['server_date', 'ip', 'temperature', 'conductivity', 'pressure', 'aux1',
#                   'aux3', 'chlorophyll', 'aux4', 'salinity', 'date',
#                   'time', 'sigmat', 'diagnosticVoltage', 'currentDraw']

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
        self.ips = {'166.148.81.45': self.staMeta['UCSB'],
       '166.241.139.252': self.staMeta['UCI'],
       '166.241.175.135': self.staMeta['UCLA'],
       '132.239.117.226': self.staMeta['UCSD'],
       '172.16.117.233': self.staMeta['UCSD']}

        self.attrArr = ['temperature', 'conductivity', 'pressure', 'aux1', 'aux3', 'chlorophyll',  # NOT INCLUDING 'time'
           'conductivity_flagPrimary', 'conductivity_flagSecondary',
           'pressure_flagPrimary', 'pressure_flagSecondary',
           'salinity_flagPrimary', 'salinity_flagSecondary',
           'chlorophyll_flagPrimary', 'chlorophyll_flagSecondary']

    def createNCshell(self, ncfile, sta):
        self.addNCshell_SCCOOS(ncfile)
        print "SASS createNCshell"
        #Move to NC/SCCOOS class???
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
            'time', np.int32, ('time'), zlib=True)  # int64? Gives error
        # time_var.setncattr({'standard_name':'time', 'long_name': 'time', 'units':'seconds since 1970-01-01 00:00:00 UTC'})
        time_var.standard_name = 'time'
        time_var.units = 'seconds since 1970-01-01 00:00:00 UTC'
        time_var.long_name = 'time'
        time_var.calendar = 'julian' #use??
        time_var.axis = "T"
        temperature = ncfile.createVariable('temperature', 'f4', ('time'), zlib=True)
        temperature.standard_name = 'sea_water_temperature'
        temperature.long_name = 'sea water temperature'
        temperature.units = 'celsius'
        temperature.coordinates = 'time lat lon depth'
        temperature.instrument = "instrument1"
        temperature_flagPrim = ncfile.createVariable(
            'temperature_flagPrimary', 'B', ('time'), zlib=True)
        temperature_flagPrim.long_name = 'sea water temperature, qc primary flag'
        temperature_flagPrim.standard_name = "sea_water_temperature status_flag"
        temperature_flagPrim.flag_values = flagPrim_flag_values
        temperature_flagPrim.flag_meanings = flagPrim_flag_meanings
        temperature_flagSec = ncfile.createVariable(
            'temperature_flagSecondary', 'B', ('time'), zlib=True)
        temperature_flagSec.long_name = 'sea water temperature, qc secondary flag'
        temperature_flagSec.flag_values = flagSec_flag_values
        temperature_flagSec.flag_meanings = flagSec_flag_meanings
        con = ncfile.createVariable('conductivity', 'f4', ('time'), zlib=True)
        con.standard_name = 'sea_water_electrical_conductivity'
        con.long_name = 'sea water electrical conductivity'
        con.units = 'S/m'
        con.coordinates = 'time lat lon depth'
        con.instrument = "instrument1"
        con_flagPrim = ncfile.createVariable(
            'conductivity_flagPrimary', 'B', ('time'), zlib=True)
        con_flagPrim.long_name = 'sea water electrical conductivity, qc primary flag'
        con_flagPrim.standard_name = "sea_water_electrical_conductivity status_flag"
        con_flagPrim.flag_values = flagPrim_flag_values
        con_flagPrim.flag_meanings = flagPrim_flag_meanings
        con_flagSec = ncfile.createVariable(
            'conductivity_flagSecondary', 'B', ('time'), zlib=True)
        con_flagSec.long_name = 'sea water electrical conductivity, qc secondary flag'
        con_flagSec.flag_values = flagSec_flag_values
        con_flagSec.flag_meanings = flagSec_flag_meanings
        pres = ncfile.createVariable('pressure', 'f4', ('time'), zlib=True)
        pres.standard_name = 'sea_water_pressure'
        pres.long_name = 'sea water pressure'
        pres.units = 'dbar'
        pres.coordinates = 'time lat lon depth'
        pres.instrument = "instrument1"
        pres_flagPrim = ncfile.createVariable(
            'pressure_flagPrimary', 'B', ('time'), zlib=True)
        pres_flagPrim.long_name = 'sea water pressure, qc primary flag'
        pres_flagPrim.standard_name = "sea_water_pressure status_flag"
        pres_flagPrim.flag_values = flagPrim_flag_values
        pres_flagPrim.flag_meanings = flagPrim_flag_meanings
        pres_flagSec = ncfile.createVariable(
            'pressure_flagSecondary', 'B', ('time'), zlib=True)
        pres_flagSec.long_name = 'sea water pressure, qc secondary flag'
        pres_flagSec.flag_values = flagSec_flag_values
        pres_flagSec.flag_meanings = flagSec_flag_meanings
        a1 = ncfile.createVariable('aux1', 'f4', ('time'), zlib=True)
        a1.long_name = 'Auxiliary 1'  # Use Standard name for 1,3,4???
        a1.units = 'V'
        a1.coordinates = 'time lat lon depth'
        a3 = ncfile.createVariable('aux3', 'f4', ('time'), zlib=True)
        a3.long_name = 'Auxiliary 3'
        a3.units = 'V'
        a3.coordinates = 'time lat lon depth'
        chl = ncfile.createVariable('chlorophyll', 'f4', ('time'), zlib=True)
        chl.standard_name = 'mass_concentration_of_chlorophyll_a_in_sea_water'
        chl.long_name = 'sea water chlorophyll'
        chl.units = 'ug/L'  # which CF name??
        chl.coordinates = 'time lat lon depth'
        chl.instrument = "instrument1"
        chl_flagPrim = ncfile.createVariable(
            'chlorophyll_flagPrimary', 'B', ('time'), zlib=True)
        chl_flagPrim.long_name = 'sea water chlorophyll, qc primary flag'
        chl_flagPrim.standard_name = "mass_concentration_of_chlorophyll_a_in_sea_water status_flag"
        chl_flagPrim.flag_values = flagPrim_flag_values
        chl_flagPrim.flag_meanings = flagPrim_flag_meanings
        chl_flagSec = ncfile.createVariable(
            'chlorophyll_flagSecondary', 'B', ('time'), zlib=True)
        chl_flagSec.long_name = 'sea water chlorophyll, qc secondary flag'
        chl_flagSec.flag_values = flagSec_flag_values
        chl_flagSec.flag_meanings = flagSec_flag_meanings
        a4 = ncfile.createVariable('aux4', 'f4', ('time'), zlib=True)
        a4.long_name = 'Auxiliary 4'
        a4.units = 'V'
        a4.coordinates = 'time lat lon depth'
        sal = ncfile.createVariable('salinity', 'f4', ('time'), zlib=True)
        sal.standard_name = 'sea_water_salinity'
        sal.long_name = 'sea water salinity'
        sal.units = '1e-3' #not psu??
        sal.coordinates = 'time lat lon depth'
        sal.instrument = "instrument1"
        sal_flagPrim = ncfile.createVariable(
            'salinity_flagPrimary', 'B', ('time'), zlib=True)
        sal_flagPrim.long_name = 'sea water salinity, qc primary flag'
        sal_flagPrim.standard_name = "sea_water_practical_salinity status_flag"
        sal_flagPrim.flag_values = flagPrim_flag_values
        sal_flagPrim.flag_meanings = flagPrim_flag_meanings
        sal_flagSec = ncfile.createVariable(
            'salinity_flagSecondary', 'B', ('time'), zlib=True)
        sal_flagSec.long_name = 'sea water salinity, qc secondary flag'
        sal_flagSec.flag_values = flagSec_flag_values
        sal_flagSec.flag_meanings = flagSec_flag_meanings
        sig = ncfile.createVariable('sigmat', 'f4', ('time'), zlib=True)
        sig.standard_name = 'sea_water_density'
        sig.long_name = 'sea water density'
        sig.units = 'kg/m^3'
        sig.coordinates = 'time lat lon depth'
        dV = ncfile.createVariable('diagnosticVoltage', 'f4', ('time'), zlib=True)
        dV.long_name = 'diagnostic voltage'  # NO standard name???
        dV.units = 'V'
        dV.coordinates = 'time lat lon depth'
        cDr = ncfile.createVariable('currentDraw', 'f4', ('time'), zlib=True)
        cDr.long_name = 'current draw'  # NO standard name???
        cDr.units = 'mA'
        cDr.coordinates = 'time lat lon depth'

        ncfile.variables['lat'][0] = self.staMeta[sta]['lat']
        ncfile.variables['lon'][0] = self.staMeta[sta]['lon']
        ncfile.variables['depth'][0] = self.staMeta[sta]['depth']

        #What is this for???
        nm = ncfile.createVariable('station', 'S1', 'name_strlen')
        nm.long_name = 'station_name'
        nm.cf_role = 'timeseries_id'
#        ncfile.variables['station'][:len(ips[ip]['loc'])] = list(ips[ip]['loc'])
        ncfile.variables['station'][:len(self.staMeta[sta]['loc'])] = list(self.staMeta[sta]['loc'])

        crs = ncfile.createVariable('crs', 'd')
        crs.grid_mapping_name = "latitude_longitude"; 
        crs.epsg_code = "EPSG:4326" ;
        crs.semi_major_axis = 6378137.0 ;
        crs.inverse_flattening = 298.257223563 ;
    
        instrument1 = ncfile.createVariable('instrument1', 'i')
        instrument1.make = "Seabird"
        instrument1.model = "SBE 16plus SEACAT"
        instrument1.comment = "Seabird SBE 16plus SEACAT Conductivity, Temperature, and Pressure recorder. Derived output Salinity."
    
        instrument2 = ncfile.createVariable('instrument2', 'i')
        instrument2.make = "Seapoint"
        instrument2.model = "Chlorophyll Fluorometer"
        instrument2.comment = "Seapoint Chlorophyll Fluorometer with a 0-50 ug/L gain setting."

        return ncfile

    #previously dataframe2nc
    def text2nc(self, filename,lastRecorded=None):
        columns = ['server_date', 'ip', 'temperature', 'conductivity', 'pressure', 'aux1',
                   'aux3', 'chlorophyll', 'aux4', 'salinity', 'date',
                   'time', 'sigmat', 'diagnosticVoltage', 'currentDraw']

        print 'filename', filename #for testing!!!
        # Create pandas dataframe from file
        #print time.strftime("%c"),
    
        # Read file line by line into a pnadas dataframe
        df = pd.read_csv(filename, sep='^', header=None, prefix='X',error_bad_lines=False)
          
        # Prepare a regex statement to parse the data out of each line
        re_Y = r'[1-2]\d{3}' # Year
        re_d = r'[0-3]\d' # Days in Month
        re_b = r'[A-S][a-u][b-y]' # Month as abbreviated name
        re_time = r'[0-2]\d:[0-5]\d:[0-5]\d'
        re_s = r'(?:,?#?\s+|,)' # delimiter: space with optional comma, optional pound; or comma alone
        re_serverdate = r'^('+re_Y+r'-[0-1]\d-'+re_d+'T'+re_time+'Z)' # server date
        re_ip = r'(\d{2,3}\.\d{2,3}\.\d{2,3}\.\d{2,3})' # ip address ending in ',# '
        re_attr = r'(\d+\.?\d*)' # attribute number with optional decimal
        re_date = '('+re_d+re_s+re_b+re_s+re_Y+')' # date with Mon spelled/abbreviated 
        re_attr8 = re_s.join([re_attr]*8) # 8 consecutive attribute, separated by delimiter
        re_attr3 = re_s.join([re_attr]*3) # 3 consecutive attribute, separated by delimiter
        regex = re_serverdate+re_s+re_ip+re_s+re_attr8+re_s+re_date+re_s+'('+re_time+')'+re_s+re_attr3+r'$' 
    
        # Split data into proper columns
        df = df.X0.str.extract(regex)
        # Drop any rows with NaN
        df = df.dropna()

        print df.shape, len(columns)
        # Set column names
        df.columns = columns
        # Set date_time to pandas datetime format
        dateformat = "%d %b %Y %H:%M:%S"
        df['date_time'] = pd.to_datetime(df.date+' '+df.time, format=dateformat, utc=None)
        # Make date_time an index
        df.set_index('date_time', inplace=True)
        # Drop columna that were merged
        df.drop('date', axis=1, inplace=True)
        df.drop('time', axis=1, inplace=True)
            
        # Make sure data are type float
        # (For some unknown reason we had to do this in 2 statements)
        df.loc[:,'temperature'] = df.loc[:,'temperature'].astype(float)
        df.iloc[:,3:13] = df.iloc[:,3:13].astype(float)
        
        # Force index to be a datetime. For some reason this needs to be done
        # Ex. data-20140610.dat only works when this is done.
        df.index = pd.to_datetime(df.index)

        print df.shape
        print df.head()
#        print df.describe()

        for ip in self.ips.keys():
            if ip in df.ip.values:
                df2 = df.where(df.ip == ip).dropna() # Remove all possible lines with NaN
                df2.index = df2.index.tz_localize('UTC') #timezone, why?
                
                # Get proper column names for this station's dataframe.
                archive_file_name = 'sass_'+self.ips[ip]['loc']+'_archive.csv'
                archive_file = os.path.join(codedir, archive_file_name)
                df2_col = pd.read_csv(archive_file, header=None, error_bad_lines=False,
                                     parse_dates=[0], infer_datetime_format=True, skipinitialspace=True, 
                                     index_col=0)
                # Find column names to use in archive based on current dataframe's date_time index
                col_names = df2_col[:df2.index[0]][-1:].values[0].tolist()
                # Remove date and time columns
                col_names.remove('date')
                col_names.remove('time')
                # Set correct columns names for current dataframe
                df2.columns = col_names
    
                # Scale chlorophyll
                df2['chlorophyll'] = df2['chlorophyll'] * 10.0
    
                # Apply QC tests
                df3 = sassqc.qc_tests(df2)
                
                # Get location name from ip
                loc = self.ips[ip]['loc']
    
                # Get last recorded date 
                LRpd = pd.to_datetime(lastRecorded, utc=None)
    
                # Get the last time stamp recored in this location's NetCDF file.
                lastNC = os.path.join(self.ncpath, loc + '-' + str(LRpd.year) + '.nc')

                locLastRecordedTime = getLastDateNC(lastNC)
    
                # Truncate data to only that which is after last recorded time 
                df3 = df3[pd.to_datetime(df3.index,utc=None) > locLastRecordedTime ]
    
                #print str(len(df3.index)), loc,
    
                if len(df3.index) > 0:
                    # Group by Year and iterate making/appending to NetCDF files
                    # Do this IF its possible there could be previous year in the file
                    groupedYr = df3.groupby(df3.index.year)
                    for grpYr in groupedYr.indices:
                        # Check file size, nccopy to bring size down, replace original file
                        ncfilename = loc + "-" + str(grpYr) + '.nc'
                        filepath = os.path.join(self.ncpath, ncfilename)
                        self.dataToNC(filepath, df3, loc)
                        self.fileSizeChecker(filepath)
    
        # Remember what the last value in the file was and write to a file
        if len(df) > 0:
            #print " ", filename
            self.writeLastRecorded(df.index[-1:][0].strftime(self.dateformat))

    def text2nc_all(self):
        mnArr = os.listdir(logsdir)
        mnArr.sort()
        for mn in mnArr:
            mnpath = os.path.join(logsdir, mn)
            if os.path.isdir(mnpath):
                filesArr = os.listdir(mnpath)
                filesArr.sort()
                ##print "\n" + time.strftime("%c")
                for fn in filesArr:
                    startfld = time.time() # time each folder
                    filename = os.path.join(mnpath, fn)
                    ##print "\n" + fn,
                    text2nc(filename)

    def text2nc_append(self):
        looplimit = 1125
        loopCount = 1
        start = time.time()
        #print "Begin:", start
        LRstr = sass.readLastRecorded().rstrip()
        if (LRstr):
            LRdt = dt(LRstr) #Last Recorded datetime
            while LRdt.timetuple()[0:3] <= time.gmtime()[0:3]:
                # Get filename to process from last recorded datetime
                name = LRdt.strftime("%Y-%m/data-%Y%m%d.dat")
                processFile = os.path.join(sass.logsdir, name)
                
                if os.path.isfile(processFile):
                    # Get Last Recorded String to NetCDF file
                    LRstr = sass.readLastRecorded().rstrip()
                    # Add latest data to NetCDF file discarding data < LRstr
                    text2nc(processFile, LRstr)
                    
                # Increment day file and count
                LRdt = LRdt + datetime.timedelta(days=1)          
                # Increment loop count so does not keep going
                loopCount += 1
                # Check if while loop has exceeded looplimit
                if loopCount > looplimit:
                    return time.time()-start
        else:
            print "ERROR: Latest Recorded file does NOT exist!"


class CAF(SCCOOS):
    def __init__(self):
        super(CAF, self).__init__()
        #print "init caf"
#        self.logsdir = r'/data/InSitu/Burkolator/data/CarlsbadAquafarm/CAF_Latest/'
        self.logsdir = r'/data/InSitu/Burkolator/data/CarlsbadAquafarm/CAF_sorted'
#        self.ncpath = '/data/InSitu/SASS/Burkolator/netcdf'
        self.ncpath = '/home/scheim/NCobj/CAF'
#        self.fnformat = "CAF_RTproc_%Y%m%d.dat" #!!!

        self.attrArr = ['TSG_T', 'TSG_S', 'pCO2_atm', 'TCO2_mol_kg',
       'Alk_pTCO2', 'AlkS', 'calcAlk', 'calcTCO2', 'calcpCO2', 'calcCO2aq',
       'calcHCO3', 'calcCO3', 'calcOmega', 'calcpH']

    def createNCshell(self, ncfile, ignore):
        #NOT using: 'pH_aux', 'O2', 'O2sat'
        print "CAF createNCshell"
        ##Meta
        ncfile.keywords = 'EARTH SCIENCE, OCEANS, SALINITY/DENSITY, SALINITY,  OCEAN CHEMISTRY,'##!!!
        ncfile.processing_level = 'QA/QC has not been performed' ##!!!
        ncfile.ip = "132.239.92.62"
        ncfile.metadata_link = 'www.sccoos.org.progress/data-products/'
        ncfile.summary = '' ##!!!
        ncfile.project = 'Carlsbad Auqafarm'
        ncfile.processing_level = 'QA/QC has not been performed'
        ncfile.cdm_data_type = 'Station'
        ncfile.geospatial_lat_resolution = ''  # ?
        ncfile.geospatial_lon_resolution = ''  # ?
        ncfile.geospatial_vertical_units = ''  # ???
        ncfile.geospatial_vertical_resolution = ''  # ???
        ncfile.geospatial_vertical_positive = ''  # ???

        # Create Dimensions
        # unlimited axis (can be appended to).
        time_dim = ncfile.createDimension('time', None)
#        name_dim = ncfile.createDimension('name_strlen', size=25)

        #Create Variables
        time_var = ncfile.createVariable(
            'time', np.int32, ('time'), zlib=True)  # int64? Gives error
        # time_var.setncattr({'standard_name':'time', 'long_name': 'time', 'units':'seconds since 1970-01-01 00:00:00 UTC'})
        time_var.standard_name = 'time'
        time_var.units = 'seconds since 1970-01-01 00:00:00 UTC'
        time_var.long_name = 'time'
        time_var.calendar = 'julian' #use??
        time_var.axis = "T"

        temperature = ncfile.createVariable('TSG_T', 'f4', ('time'), zlib=True)
        temperature.standard_name = 'sea_water_temperature'
        temperature.long_name = 'sea water temperature'
        temperature.units = 'celsius'
        temperature.coordinates = ''
        temperature.instrument = 'instrument1'
        salinity = ncfile.createVariable('TSG_S', 'f4', ('time'), zlib=True)
        salinity.standard_name = 'sea_water_salinity'
        salinity.long_name = 'sea water salinity'
        salinity.units = 'psu' #?
        salinity.coordinates = ''
        salinity.instrument = 'instrument1'
        pCO2_atm = ncfile.createVariable('pCO2_atm', 'f4', ('time'), zlib=True)
        pCO2_atm.standard_name = 'surface_partial_pressure_of_carbon_dioxide_in_sea_water' #surface?
        pCO2_atm.long_name = 'Partial pressure of carbon dioxide'
        pCO2_atm.units = 'uatm'
        pCO2_atm.coordinates = ''
        pCO2_atm.instrument = 'instrument1'
        TCO2m = ncfile.createVariable('TCO2_mol_kg', 'f4', ('time'), zlib=True)
        TCO2m.standard_name = 'mole_concentration_of_dissolved_inorganic_carbon_in_sea_water'
        TCO2m.long_name = 'Total Inorganic Carbon'
        TCO2m.units = 'umol/kg'
        TCO2m.coordinates = ''
        TCO2m.instrument = 'instrument1'
        alkpTCO2 = ncfile.createVariable('Alk_pTCO2', 'f4', ('time'), zlib=True)
        #alkpTCO2.standard_name = ''
        alkpTCO2.long_name = 'total alkalinity estimated via pCO2/TCO2 measurements'
        alkpTCO2.units = 'umol/kg'
        #alkpTCO2.coordinates = ''
        alkpTCO2.instrument = 'instrument1'
        alkS = ncfile.createVariable('AlkS', 'f4', ('time'), zlib=True)
        #alkS.standard_name = '' #sea_water_alkalinity_expressed_as_mole_equivalent
        alkS.long_name = 'total alkalinity estimated via salinity measurements'
        alkS.units = 'umol/kg'
        #alkS.coordinates = ''
        alkS.instrument = 'instrument1'
        calcAlk = ncfile.createVariable('calcAlk', 'f4', ('time'), zlib=True)
        #calcAlk.standard_name = ''
        calcAlk.long_name = 'calculated total alkalinity'
        calcAlk.units = 'umol/kg'
        #calcAlk.coordinates = ''
        calcAlk.instrument = 'instrument1'
        calcTCO2 = ncfile.createVariable('calcTCO2', 'f4', ('time'), zlib=True)
        #calcTCO2.standard_name = ''
        calcTCO2.long_name = 'calculated total dissolved inorganic carbon'
        calcTCO2.units = 'umol/kg'
        #calcTCO2.coordinates = ''
        calcTCO2.instrument = 'instrument1'
        calcpCO2 = ncfile.createVariable('calcpCO2', 'f4', ('time'), zlib=True)
        #calcpCO2.standard_name = ''
        #calcpCO2.long_name = 'calculated partial pressure of CO2'
        calcpCO2.units = 'uatm'
        #calcpCO2.coordinates = ''
        calcpCO2.instrument = 'instrument1'
        calcCO2aq = ncfile.createVariable('calcCO2aq', 'f4', ('time'), zlib=True)
        #calcCO2aq.standard_name = ''
        #calcCO2aq.long_name = ''
        #calcCO2aq.units = ''
        #calcCO2aq.coordinates = ''
        #calcCO2aq.instrument = 'instrument1'
        calcHCO3 = ncfile.createVariable('calcHCO3', 'f4', ('time'), zlib=True)
        #calcHCO3.standard_name = ''
        calcHCO3.long_name = 'calculated concentration of bicarbonate ion'
        calcHCO3.units = 'umol/kg'
        #calcHCO3.coordinates = ''
        calcHCO3.instrument = 'instrument1'
        calcCO3 = ncfile.createVariable('calcCO3', 'f4', ('time'), zlib=True)
        #calcCO3.standard_name = ''
        calcCO3.long_name = 'calculated concentration of carbonate ion'
        calcCO3.units = 'umol/kg'
        #calcCO3.coordinates = ''
        calcCO3.instrument = 'instrument1'
        calcOmega = ncfile.createVariable('calcOmega', 'f4', ('time'), zlib=True)
        #calcOmega.standard_name = ''
        calcOmega.long_name = 'calculated aragonite saturation state'
        #calcOmega.units = ''
        #calcOmega.coordinates = ''
        calcOmega.instrument = 'instrument1'
        calcpH = ncfile.createVariable('calcpH', 'f4', ('time'), zlib=True)
        #calcpH.standard_name = ''
        calcpH.long_name = 'calculated pH'
        #calcpH.units = ''
        #calcpH.coordinates = ''
        calcpH.instrument = 'instrument1'

        # = ncfile.createVariable('', 'f4', ('time'), zlib=True)
        #.standard_name = ''
        #.long_name = ''
        #.units = ''
        #.coordinates = ''
        #.instrument = 'instrument1'

        #for c in cols:
        #    cVar = ncfile.createVariable(c, 'f4', ('time'), zlib=True)
        #    cVar.long_name = c

        instrument1 = ncfile.createVariable('instrument1', 'i') #Licor??
        instrument1.make = ""
        instrument1.model = ""
        instrument1.comment = "beta Burkelator" #?

        return ncfile

    def text2nc(self, filename,lastRecorded=None):
        print 'IN text2nc, filename:', filename #for testing!!! 

        # Read file line by line into a pnadas dataframe
        df = pd.read_csv(filename, sep="\s+", header=2, dtype={'Date':object, 'Time':object})

        # Set date_time to pandas datetime format
        dateformat = "%Y%m%d %H%M%S"
        df['date_time'] = pd.to_datetime(df['Date']+' '+df['Time'], format=dateformat, utc=None)
        # Make date_time an index
        df.set_index('date_time', inplace=True)
        # Drop columna that were merged
        df.drop('Date', axis=1, inplace=True)
        df.drop('Time', axis=1, inplace=True)
        df.columns = map(lambda x: x.replace('\xb5', ''), df.columns)
        #self.attrArr = df.columns

        #print df.head()
        #print df.dtypes
        if len(df.index) > 0:
            # Group by Year and iterate making/appending to NetCDF files
            # Do this IF its possible there could be previous year in the file
            groupedYr = df.groupby(df.index.year) # is this necessary or can we just grab the year?
            for grpYr in groupedYr.indices:
                # Check file size, nccopy to bring size down, replace original file
                ncfilename = "CAF-" + str(grpYr) + '.nc'
                filepath = os.path.join(self.ncpath, ncfilename)
                self.dataToNC(filepath, df, '')
                self.fileSizeChecker(filepath)

    def text2nc_all(self):
        yrArr = os.listdir(self.logsdir)
        yrArr.sort()
        for yr in yrArr:
            yrpath = os.path.join(self.logsdir, yr)
            if os.path.isdir(yrpath):
                filesArr = os.listdir(yrpath)
                filesArr.sort()
                for fn in filesArr:
                    print fn
                    if fn.startswith('CAF_RTproc_'):
                        filepath = os.path.join(yrpath, fn)
                        CAF().text2nc(filepath)                

    def text2nc_append(self):
        pass

#s = SASS()
#print s.ncpath
#tmpFile = os.path.join(s.ncpath, 'test.nc')
#ncfile = Dataset(tmpFile, 'w', format='NETCDF4')
#sta = 'UCSD'
##ncfile = s.createNCshell(ncfile, sta)
##print ncfile
#testTxt = os.path.join(s.logsdir, '2016-06','data-20160601.dat')
#print testTxt
#print "if file", os.path.isfile(testTxt)
#s.text2nc(testTxt)

c = CAF()
testTxt = os.path.join(c.logsdir, 'CAF_RTproc_201605240042')
print testTxt
print "if file", os.path.isfile(testTxt)
#c.text2nc(testTxt)
c.text2nc_all()

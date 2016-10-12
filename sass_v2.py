#
# Author Sarah Heim
# Date create: 2016
# Description: adjusting to class/objects, inheriting NC/SASS classes
#   This class is created for Automated Shore Stations
#
import os, time, datetime

import pandas as pd
import numpy as np
# from netCDF4 import Dataset
# from abc import ABCMeta, abstractmethod

import sccoos
import sassqc, qc #transition sassqc to qc

class SASS(sccoos.SCCOOS):
    """Class for SCCOOS's Automated Shore Stations. Currently, log files and netCDFs"""
    #set SASS metadata
    def __init__(self):
        """Setting up SASS variables

        .. todo::
            - change ncpath (currently local for testing)
            - move metadata to external text file(s)?
        """
        super(SASS, self).__init__()
        #print "init sass"
        self.logsdir = r'/data/InSitu/SASS/raw_data/'
#        self.ncpath = '/data/InSitu/SASS/netcdfs_new/'
        self.ncpath = '/home/scheim/NCobj/SASS'
        self.codedir = '/data/InSitu/SASS/code/NCobj'
        self.crontab = True
        self.txtFnformat = "%Y-%m/data-%Y%m%d.dat" #!!! Where is this used?

#        self.columns = ['server_date', 'ip', 'temperature', 'conductivity', 'pressure', 'aux1',
#                   'aux3', 'chlorophyll', 'aux4', 'salinity', 'date',
#                   'time', 'sigmat', 'diagnosticVoltage', 'currentDraw']

        self.staMeta = {'loc': 'newport_pier',
                   'loc_name': 'Newport Pier',
                   'lat': 33.6061,
                   'lon': -117.9311,
                   'depth': '2',
                   'abbr':'UCI',
                   'url': 'http://uci.edu/',
                   'inst': 'University of California, Irvine'}

        # IP Address of Shorestations, connecting to appropriate self.staMeta dictionary
    #     self.ips = {'166.241.139.252': self.staMeta['newport_pier'],
    #    '166.140.102.113': self.staMeta['newport_pier']}

       # NOT INCLUDING 'time'
        self.attrArr = ['temperature', 'conductivity', 'pressure', 'salinity', 'chlorophyll',
            'O2thermistor', 'convertedOxygen',
            'temperature_flagPrimary', 'temperature_flagSecondary',
            'conductivity_flagPrimary', 'conductivity_flagSecondary',
            'pressure_flagPrimary', 'pressure_flagSecondary',
            'salinity_flagPrimary', 'salinity_flagSecondary',
            'chlorophyll_flagPrimary', 'chlorophyll_flagSecondary',
            'sigmat', 'diagnosticVoltage', 'currentDraw']

        self.metaDict.update({
            ##Meta
            'cdm_data_type':'Station',
            'contributor_role': 'station operation, station funding, data management',
            'geospatial_lat_resolution':'2.77E-4',
            'geospatial_lon_resolution':'2.77E-4',
            'geospatial_vertical_units':'m',
            'geospatial_vertical_resolution':'1',
            'geospatial_vertical_positive':'down',
            'keywords':'EARTH SCIENCE, OCEANS, SALINITY/DENSITY, SALINITY,  OCEAN CHEMISTRY,' +\
            ' CHLOROPHYLL, OCEAN TEMPERATURE, WATER TEMPERATURE, OCEAN PRESSURE, WATER PRESSURE',
            'metadata_link':'www.sccoos.org.progress/data-products/automateed-shore-stations/',
            'project':'Automated Shore Stations',
            'processing_level':'QA/QC have been performed',
            'summary':'Automated shore station with a suite of sensors that are' +\
            ' attached to piers along the nearshore California coast.' + \
            ' These automated sensors measure temperature, salinity, chlorophyll, turbidity' + \
            ' and water level at frequent intervals in the nearshore coastal ocean.' +\
            ' This data can provide local and regional information on mixing and upwelling,' +\
            ' land run-off, and algal blooms.'
            })

    def createNCshell(self, ncfile, sta):
        """
        .. todo::
            - add more history for stations
            - move createVariables to external text file??
        """
        print "SASS createNCshell", ncfile
        self.metaDict.update({
        'comment': 'The '+self.staMeta['loc_name']+' automated shore station operated' + \
        ' by ' + self.staMeta['inst'] + \
        ' is mounted at a nominal depth of '+ self.staMeta['depth'] +' meters MLLW. The' + \
        ' instrument package includes a Seabird SBE 16plus SEACAT Conductivity,' + \
        ' Temperature, and Pressure recorder, and a Seapoint Chlorophyll Fluorometer' + \
        ' with a 0-50 ug/L gain setting.',
        'contributor_name': self.staMeta['abbr']+'/SCCOOS, SCCOOS/IOOS/NOAA, SCCOOS',
        'creator_name': self.staMeta['inst'],
        'creator_url': self.staMeta['url'],
        "date_created": self.tupToISO(time.gmtime()), #time.ctime(time.time()),
        "geospatial_lat_min": self.staMeta['lat'],
        "geospatial_lat_max": self.staMeta['lat'],
        "geospatial_lon_min": self.staMeta['lon'],
        "geospatial_lon_max": self.staMeta['lon'],
        "geospatial_vertical_min": self.staMeta['depth'],
        "geospatial_vertical_max": self.staMeta['depth'],
        "history": "Created: "+ self.tupToISO(time.gmtime()), #time.ctime(time.time()),
        "title":self.metaDict["project"]+": "+self.staMeta['loc_name'],
        })
        ncfile.setncatts(self.metaDict)
        #Move to NC/SCCOOS class???
        flagPrim_flag_values = bytearray([1, 2, 3, 4, 9]) # 1UB, 2UB, 3UB, 4UB, 9UB ;
        flagPrim_flag_meanings = 'GOOD_DATA UNKNOWN SUSPECT BAD_DATA MISSING'
        flagSec_flag_values = bytearray([0, 1, 2, 3]) # 1UB, 2UB, 3UB, 4UB, 9UB ;
        flagSec_flag_meanings = 'UNSPECIFIED RANGE FLAT_LINE SPIKE'

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
        time_var.calendar = 'julian'
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

        o2 = ncfile.createVariable('O2thermistor', 'f4', ('time'), zlib=True)
        # o2.standard_name = ''
        o2.long_name = 'O2 thermistor'
        o2.units = 'V' #not psu??
        o2.coordinates = 'time lat lon depth'
        o2.instrument = "instrument3"
        o2_flagPrim = ncfile.createVariable(
            'O2_flagPrimary', 'B', ('time'), zlib=True)
        o2_flagPrim.long_name = ', qc primary flag'
        # o2_flagPrim.standard_name = " status_flag"
        o2_flagPrim.flag_values = flagPrim_flag_values
        o2_flagPrim.flag_meanings = flagPrim_flag_meanings
        o2_flagSec = ncfile.createVariable(
            'O2_flagSecondary', 'B', ('time'), zlib=True)
        o2_flagSec.long_name = ', qc secondary flag'
        o2_flagSec.flag_values = flagSec_flag_values
        o2_flagSec.flag_meanings = flagSec_flag_meanings

        conv = ncfile.createVariable('convertedOxygen', 'f4', ('time'), zlib=True)
        # conv.standard_name = 'mass_concentration_of_oxygen_in_sea_water'
        conv.long_name = 'converted_oxygen'
        conv.units = 'mL/L' #not psu??
        conv.coordinates = 'time lat lon depth'
        conv.instrument = "instrument3"
        conv_flagPrim = ncfile.createVariable(
            'converted_oxygen_flagPrimary', 'B', ('time'), zlib=True)
        conv_flagPrim.long_name = ', qc primary flag'
        # conv_flagPrim.standard_name = " status_flag"
        conv_flagPrim.flag_values = flagPrim_flag_values
        conv_flagPrim.flag_meanings = flagPrim_flag_meanings
        conv_flagSec = ncfile.createVariable(
            'converted_oxygen_flagSecondary', 'B', ('time'), zlib=True)
        conv_flagSec.long_name = ', qc secondary flag'
        conv_flagSec.flag_values = flagSec_flag_values
        conv_flagSec.flag_meanings = flagSec_flag_meanings


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

        #What is this for???
        nm = ncfile.createVariable('station', 'S1', 'name_strlen')
        nm.long_name = 'station_name'
        nm.cf_role = 'timeseries_id'
#        ncfile.variables['station'][:len(ips[ip]['loc'])] = list(ips[ip]['loc'])
        ncfile.variables['station'][:len(self.staMeta['loc'])] = list(self.staMeta['loc'])

        crs = ncfile.createVariable('crs', 'd')
        crs.grid_mapping_name = "latitude_longitude";
        crs.epsg_code = "EPSG:4326" ;
        crs.semi_major_axis = 6378137.0 ;
        crs.inverse_flattening = 298.257223563 ;

        instrument1 = ncfile.createVariable('instrument1', 'i')
        instrument1.make = "Seabird"
        instrument1.model = "SBE 16plus SEACAT"
        instrument1.comment = "Seabird SBE 16plus SEACAT Conductivity, Temperature," + \
        " and Pressure recorder. Derived output Salinity."
        instrument1.ioos_code = "urn:ioos:sensor:sccoos:"+self.staMeta['loc']+":conductivity_temperature_pressure"

        instrument2 = ncfile.createVariable('instrument2', 'i')
        instrument2.make = "Seapoint"
        instrument2.model = "Chlorophyll Fluorometer"
        instrument2.comment = "Seapoint Chlorophyll Fluorometer with a 0-50 ug/L gain setting."
        instrument2.ioos_code = "urn:ioos:sensor:sccoos:"+self.staMeta['loc']+":chlorophyll"

        instrument3 = ncfile.createVariable('instrument3', 'i')
        # instrument3.make = ""
        # instrument3.model = ""
        # instrument3.comment = ""
        instrument3.ioos_code = "urn:ioos:sensor:sccoos:"+self.staMeta['loc']+":chlorophyll"

        platform1 = ncfile.createVariable('platform1', 'i')
        platform1.long_name = self.staMeta['loc_name']
        platform1.ioos_code = "urn:ioos:sensor:sccoos:"+self.staMeta['loc']

        self.addNCshell_SCCOOS(ncfile)
        ncfile.variables['lat'][0] = self.staMeta['lat']
        ncfile.variables['lon'][0] = self.staMeta['lon']
        ncfile.variables['depth'][0] = self.staMeta['depth']

        return ncfile

    def text2nc(self, filename):
        """#previously dataframe2nc
        - Uses Panda's ``read_csv``
        - Does a series of regular expressions (a.k.a. regex)
        - Uses QC methods from **sassqc**

        .. warning: sassqc getting ``SettingWithCopyWarning``?
        """
        #used just for date, time
        # columns = ['server_date', 'ip', 'temperature', 'conductivity', 'pressure',
        #            'chlorophyll', 'o2', 'convertedOxygen', 'salinity', 'date',
        #            'time', 'sigmat', 'diagnosticVoltage', 'currentDraw']

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
        re_attr = r'(-?\d+\.?\d*)' # attribute number with: optional decimal, optional negative
        re_date = '('+re_d+re_s+re_b+re_s+re_Y+')' # date with Mon spelled/abbreviated
        re_attr7 = re_s.join([re_attr]*7) # 7 consecutive attribute, separated by delimiter
        re_attr3 = re_s.join([re_attr]*3) # 3 consecutive attribute, separated by delimiter
        regex = re_serverdate+re_s+re_ip+re_s+re_attr7+re_s+re_date+re_s+'('+re_time+')'+re_s+re_attr3+r'$'

        # Split data into proper columns
        df = df.X0.str.extract(regex)

        # Drop any rows with NaN
        df = df.dropna()

        # Get proper column names for this station's dataframe.
        archive_file_name = 'sass_'+self.staMeta['loc']+'_archive.csv'
        archive_file = os.path.join(self.codedir, archive_file_name)
        # archive_file = archive_file_name
        df_col = pd.read_csv(archive_file, header=None, error_bad_lines=False,
                             parse_dates=[0], infer_datetime_format=True, skipinitialspace=True,
                             index_col=0)
        #print df_col.describe()

        #print df.index[0]
        # Find column names to use in archive based on current dataframe's date_time index
        # col_names = df_col[:df.index[0]][-1:].values[0].tolist()
        # removed nan: if a row is shorter than others
        # col_names = df_col[:df.index[0]][-1:].dropna(axis=1).values[0].tolist()
        # !!!!!!!!!!!!!!TEMPORARY!!!!!!!!!!!!!!!
        col_names = df_col[:][-1:].dropna(axis=1).values[0].tolist()
        # print col_names
        # Remove date and time columns
        # col_names.remove('date')
        # col_names.remove('time')
        # Set correct columns names for current dataframe
        df.columns = col_names

        # Set column names
        # df.columns = columns
        # Set date_time to pandas datetime format
        dateformat = "%d %b %Y %H:%M:%S"
        df['date_time'] = pd.to_datetime(df.date+' '+df.time, format=dateformat, utc=None)
        # Make date_time an index
        df.set_index('date_time', inplace=True)
        # Drop columna that were merged
        df.drop('date', axis=1, inplace=True)
        df.drop('time', axis=1, inplace=True)
        # Force index to be a datetime. For some reason this needs to be done
        # Ex. data-20140610.dat only works when this is done.
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize('UTC') #timezone, why?

        # print 'df.head:', df.head()
        # print 'df.shape:', df.shape
#        print 'df.describe:',df.describe()

        # Make sure data are type float
        # (For some unknown reason we had to do this in 2 statements)
        df.loc[:,'temperature'] = df.loc[:,'temperature'].astype(float)
        df.iloc[:,3:12] = df.iloc[:,3:12].astype(float)

        # Scale chlorophyll
        #df['chlorophyll'] = df['chlorophyll'] * 10.0 #SettingWithCopyWarning
        #df.loc[:,'chlorophyll'] = df.loc[:,'chlorophyll'] * 10.0
        df['chlorophyll'].apply(lambda x: x*10)

        # Apply QC tests
        # df = sassqc.qc_tests(df)
        # ## Replace qc testing lines, add missing value
        df = self.qc_tests(df, 'temperature', sensor_span=(-5,30), user_span=(8,30),
        low_reps=2, high_reps=6, eps=0.0001, low_thresh=2, high_thresh=3)
        df = self.qc_tests(df, 'conductivity', sensor_span=(0,9), user_span=None,
        low_reps=2, high_reps=5, eps=0.00005, low_thresh=None, high_thresh=None)
        df = self.qc_tests(df, 'pressure', sensor_span=(0,20), user_span=(1,7),
        low_reps=2, high_reps=5, eps=0.0005, low_thresh=4, high_thresh=5)
        df = self.qc_tests(df, 'salinity', sensor_span=(2,42), user_span=(30,34.5),
        low_reps=3, high_reps=5, eps=0.00004, low_thresh=0.4, high_thresh=0.5)
        df = self.qc_tests(df, 'chlorophyll', sensor_span=(0.02,50), user_span=(0.02,50),
        low_reps=2, high_reps=5, eps=0.001, low_thresh=0.8, high_thresh=1.0)

        ## Get the last time stamp recored in this location's NetCDF file.
        lastNC = self.getLastNC(self.staMeta['loc'] + '-')

        # Truncate data to only that which is after last recorded time
        pd_getLastDateNC = pd.to_datetime(self.getLastDateNC(lastNC), unit='s', utc=None)
        df = df[pd.to_datetime(df.index,utc=None) > pd_getLastDateNC ]

        print str(len(df.index)), self.staMeta['loc']

        if len(df.index) > 0:
            # Group by Year and iterate making/appending to NetCDF files
            # Do this IF its possible there could be previous year in the file
            groupedYr = df.groupby(df.index.year)
            for grpYr in groupedYr.indices:
                # Check file size, nccopy to bring size down, replace original file
                ncfilename = self.staMeta['loc'] + "-" + str(grpYr) + '.nc'
                filepath = os.path.join(self.ncpath, ncfilename)
                self.dataToNC(filepath, df, self.staMeta['loc'])
                self.fileSizeChecker(filepath)

    def text2nc_all(self):
        mnArr = os.listdir(self.logsdir)
        mnArr.sort()
        for mn in mnArr:
            mnpath = os.path.join(self.logsdir, mn)
            if os.path.isdir(mnpath):
                filesArr = os.listdir(mnpath)
                filesArr.sort()
                ##print "\n" + time.strftime("%c")
                for fn in filesArr:
                    startfld = time.time() # time each folder
                    filename = os.path.join(mnpath, fn)
                    print "\n" + fn,
                    self.text2nc(filename)


    def text2nc_append(self):
        """SASS log files are organized by server date (when recorded)"""
        looplimit = 100
        loopCount = 1
        # latestDict = {}
        # for loc in self.staMeta:
        lastNC = self.getLastNC(self.staMeta['loc'] + '-')
        lastest = self.getLastDateNC(lastNC)
        LRdt = datetime.datetime.utcfromtimestamp(lastest)
        print 'MAX, last recorded', LRdt
        while LRdt.timetuple()[0:3] <= time.gmtime()[0:3]:
            # Get filename to process from last recorded datetime
            name = LRdt.strftime("%Y-%m/data-%Y%m%d.dat")
            print name
            processFile = os.path.join(self.logsdir, name)
            if os.path.isfile(processFile):
                # Add latest data to NetCDF file discarding data < LRstr
                self.text2nc(processFile)

            # Increment day file and count
            LRdt = LRdt + datetime.timedelta(days=1)
            # Increment loop count so does not keep going
            loopCount += 1
            # Check if while loop has exceeded looplimit
            if loopCount > looplimit:
                return time.time()-start

#s = SASS()
#print s.ncpath
#s.text2nc_all()
#s.text2nc_append()

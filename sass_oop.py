#
# Author Sarah Heim
# Date create: 2016
# Description: adjusting to class/objects, inheriting NC/SASS classes
#   This class is created for Automated Shore Stations
#
import os, time, datetime, json, math, re

import pandas as pd
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from abc import ABCMeta, abstractmethod

import sccoos
import sassqc #, qc #transition sassqc to qc

class Station(object):
    def __init__(self, **kwargs):
        allowed_keys = set(['code_name','long_name','wmo','dpmt', 'ips', 'lat','lon','depth',
            'abbr','url','inst'])
        # initialize all allowed keys to false
        self.__dict__.update((key, False) for key in allowed_keys)
        # and update the given keys by their given values
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)

    def __repr__(self):
        return "Station(code_name='{}', long_name='{}', ips=['{}'])".format(self.code_name, self.long_name, self.ips)

    def __str__(self):
        return self.__dict__

#Stations
ucsb = Station(code_name = 'stearns_wharf',
                long_name= 'Stearns Wharf',
                wmo='TNWC1',
                ips= ['166.148.81.45'],
                lat= 34.408,
                lon= -119.685,
                depth= 2,
                abbr='UCSB',
                url= 'http://msi.ucsb.edu/',
                inst= 'Marine Science Institute at University of California, Santa Barbara')
uci = Station(code_name = 'newport_pier',
                long_name = 'Newport Pier',
                wmo = 'NEPC1',
                ips= ['166.241.139.252','166.140.102.113'],
                lat= 33.6061,
                lon= -117.9311,
                depth= 2,
                abbr='UCI',
                url= 'http://uci.edu/',
                inst= 'University of California, Irvine')
ucla = Station(code_name= 'santa_monica_pier',
                long_name= 'Santa Monica Pier',
                ips= ['166.241.175.135'],
                lat= 34.008,
                lon= -118.499,
                depth= 2,
                abbr='UCLA',
                url= 'http://environment.ucla.edu/',
                inst= 'Institute of the Environment at University of California, Los Angeles')
ucsd = Station(code_name = 'scripps_pier',
                long_name = 'Scripps Pier',
                wmo = 'LJSC1',
                ips= ['132.239.117.226', '172.16.117.233'],
                lat= 32.867,
                lon= -117.257,
                depth= 5,
                abbr='UCSD',
                url= 'http://sccoos.org/',
                inst= 'Southern California Coastal Ocean Observing System (SCCOOS) at Scripps Institution of Oceanography (SIO)')

uci2 = Station(code_name = '005_newport_pier',
                long_name = 'Newport Pier',
                # wmo = 'NEPC1',
                ips= ['132.239.92.8', '166.140.102.113'],
                lat= 33.6061,
                lon= -117.9311,
                depth= 2,
                abbr='UCI',
                url= 'http://uci.edu/',
                inst= 'University of California, Irvine')

class SASS(sccoos.SCCOOS):
    """Class for SCCOOS's Automated Shore Stations. Currently, log files and netCDFs

    :attr str codedir: location of code to use
    :attr str ncpath: location of netCDFs
    :attr bool crontab:
    :attr arr calcArr: array of calculations to be done in ORDER to be done
    :attr dict metaDict: dictionary of metadata to put in netCDF global attribute

    Move note to nc/sccoos.py?
    ``self.attrObjArr``: string of names of variables
    ``self.attrArr``: list of objects (use this.name)
    """
    #set SASS metadata
    @abstractmethod
    def __init__(self, sta):
        self.sta = sta
        print "init SASS", self.sta.code_name
        """Setting up SASS

        .. todo::
            - (meta) Add creator_institution. 'inst' is creator_name (change?).

        :param str filename: filename, including directory location
        """
        super(SASS, self).__init__()
        #print "init sass"

        # #test locations
        self.codedir = '/home/scheim/NCobj/'
        # self.ncpath = '/home/scheim/NCobj/SASS_new'
        # self.ncpath = '/data/Junk/thredds-test/sass_meta'

        # self.codedir = '/data/InSitu/SASS/code/ncobjects'
        self.ncpath = '/data/InSitu/SASS/netcdfs_new/'

        # self.dateformat = '%Y-%m-%dT%H:%M:%S.%fZ'
        self.crontab = True
        self.calcArr = ['chlorophyll']

        self.metaDict.update({
            'cdm_data_type':'Station',
            'contributor_role': 'station operation, station funding, data management',
            'geospatial_lat_resolution':'2.77E-4',
            'geospatial_lon_resolution':'2.77E-4',
            'geospatial_vertical_units':'m',
            'geospatial_vertical_resolution':'1',
            'geospatial_vertical_positive':'down',
            'keywords':'EARTH SCIENCE, OCEANS, OCEAN CHEMISTRY, SALINITY/DENSITY, SALINITY,' +\
            ' CHLOROPHYLL, OCEAN TEMPERATURE, WATER TEMPERATURE, OCEAN PRESSURE, WATER PRESSURE',
            'metadata_link':'http://sccoos.org/data/autoss/',
            'project':'Automated Shore Stations',
            'processing_level':'QA/QC have been performed',
            'instrument': 'In Situ/Laboratory Instruments > Profilers/Sounders > > > CTD',
            'instrument_vocabulary': 'GCMD Earth Science Keywords. Version 8.5',
            'platform': 'In Situ Ocean-based Platforms > OCEAN PLATFORM/OCEAN STATIONS > OCEAN PLATFORMS',
            'platform_vocabulary': 'GCMD Earth Science Keywords. Version 8.5',
            'references':'http://sccoos.org/data/autoss/, http://sccoos.org/about/dmac/, https://github.com/ioos/qartod',
            })

        #Attributes
        self.attr_time = MainAttr('time',
            dtype=np.int32,
            atts={
                'axis':"T",
                'calendar':'julian',
                'comment':'also known as Epoch or Unix time',
                'long_name':'time',
                'standard_name':'time',
                'units':'seconds since 1970-01-01 00:00:00 UTC',
                'platform': "platform1"
            })
        self.attr_temp = MainAttr('temperature',
            dtype= 'f4',
            atts={
                'standard_name' : 'sea_water_temperature',
                'long_name' : 'sea water temperature',
                'ncei_name': 'WATER TEMPERATURE',
                'units' : 'celsius',
                'instrument' : "instrument1",
                'platform': "platform1"
            },
            qc={
                'sensor_span':(-5,30), 'user_span':(8,30),
                'low_reps':4, 'high_reps':7, 'eps':0.00005, 'low_thresh':2, 'high_thresh':3
                # , 'rec_time_col':'server_date', 'delay':60000, 'time_interval':1000
            })
        self.attr_tempF1 = FlagAttr('temperature_flagPrimary',
            atts={
                'long_name' : 'sea water temperature, qc primary flag',
                'standard_name' : "sea_water_temperature status_flag"
            })
        self.attr_tempF2 = FlagAttr('temperature_flagSecondary',
            atts={
                'long_name' : 'sea water temperature, qc secondary flag',
                'standard_name' : "sea_water_temperature status_flag"
            })
        self.attr_con = MainAttr('conductivity',
            dtype= 'f4',
            atts={
                'standard_name' : 'sea_water_electrical_conductivity',
                'long_name' : 'sea water electrical conductivity',
                'ncei_name': 'CONDUCTIVITY',
                'units' : 'S/m',
                'instrument' : "instrument1",
                'platform': "platform1"
            },
            qc={
                'sensor_span':(0,9), 'user_span':None,
                'low_reps':4, 'high_reps':7, 'eps':0.00001, 'low_thresh':None, 'high_thresh':None
            })
        self.attr_conF1 = FlagAttr('conductivity_flagPrimary',
            atts={
                'long_name' : 'sea water electrical conductivity, qc primary flag',
                'standard_name' : "sea_water_electrical_conductivity status_flag"
            })
        self.attr_conF2 = FlagAttr('conductivity_flagSecondary',
            atts={
                'long_name' : 'sea water electrical conductivity, qc secondary flag',
                'standard_name' : "sea_water_electrical_conductivity status_flag"
            })
        self.attr_pres = MainAttr('pressure',
            dtype= 'f4',
            atts={
                'standard_name' : 'sea_water_pressure',
                'long_name' : 'sea water pressure',
                'ncei_name': 'PRESSURE - WATER',
                'units' : 'dbar',
                'instrument' : "instrument1",
                'platform': "platform1"
            },
            qc={
                'sensor_span':(0,20), 'user_span':(1,7),
                'low_reps':6, 'high_reps':10, 'eps':0.0005, 'low_thresh':4, 'high_thresh':5
            })
        self.attr_presF1 = FlagAttr('pressure_flagPrimary',
            atts={
                'long_name' : 'sea water pressure, qc primary flag',
                'standard_name' : "sea_water_pressure status_flag"})
        self.attr_presF2 = FlagAttr('pressure_flagSecondary',
            atts={
                'long_name' : 'sea water pressure, qc secondary flag',
                'standard_name' : "sea_water_pressure status_flag"
            })

        self.attr_sal = MainAttr('salinity',
            dtype= 'f4',
            atts={
                'standard_name' : 'sea_water_salinity',
                'long_name' : 'sea water salinity',
                'ncei_name': 'SALINITY',
                'units' : '1e-3', #PSU?
                'instrument' : "instrument1",
                'platform': "platform1"
            },
            qc={
                'sensor_span':(2,42), 'user_span':(30,34.5),
                'low_reps':6, 'high_reps':9, 'eps':0.00005, 'low_thresh':4, 'high_thresh':5
            })
        self.attr_salF1 = FlagAttr('salinity_flagPrimary',
            atts={
                'long_name' : 'sea water salinity, qc primary flag',
                'standard_name' : "sea_water_practical_salinity status_flag"
        })
        self.attr_salF2 = FlagAttr('salinity_flagSecondary',
            atts={
                'long_name' : 'sea water salinity, qc secondary flag',
                'standard_name' : "sea_water_practical_salinity status_flag"
        })
        # self.attr_chl= MainAttr('chlorophyll',
        #     dtype= 'f4',
        #     atts={
        #         'standard_name' : 'mass_concentration_of_chlorophyll_a_in_sea_water',
        #         'long_name' : 'sea water chlorophyll',
        #         'units' : 'ug/L',
        #         'instrument' : "instrument2"
        #     },
        #     sensor_span=(0.02,50), user_span=(0.02,50),
        #     low_reps=2, high_reps=5, eps=0.001, low_thresh=0.8, high_thresh=1.0)
        self.attr_chl1= MainAttr('chlorophyll_raw',
            dtype= 'f4',
            atts={
                'standard_name' : 'mass_concentration_of_chlorophyll_a_in_sea_water',
                'long_name' : 'sea water chlorophyll',
                'units' : 'ug/L',
                'instrument' : "instrument2",
                'platform': "platform1",
                'valid_min': np.float32(0),
                'valid_max': np.float32(5)
            })
        self.attr_chl2= MainAttr('chlorophyll',
            dtype= 'f4',
            atts={
                'standard_name' : 'mass_concentration_of_chlorophyll_a_in_sea_water',
                'long_name' : 'sea water chlorophyll',
                'ncei_name': 'CHLOROPHYLL', #??? 'CHLOROPHYLL - EXTRACTED', 'NANOPLANKTON - CHLOROPHYLL'
                'units' : 'ug/L',
                'instrument' : "instrument2",
                'platform': "platform1"
            },
            qc={
                'sensor_span':(0.02,50), 'user_span':(0.02,50),
                'low_reps':6, 'high_reps':10, 'eps':0.0005, 'low_thresh':0.8, 'high_thresh':1.0
            })
        self.attr_chlF1 = FlagAttr('chlorophyll_flagPrimary',
            atts={
                'long_name' : 'sea water chlorophyll, qc primary flag',
                'standard_name' : "mass_concentration_of_chlorophyll_a_in_sea_water status_flag"})
        self.attr_chlF2 = FlagAttr('chlorophyll_flagSecondary',
            atts={
                'long_name' : 'sea water chlorophyll, qc secondary flag',
                'standard_name' : "mass_concentration_of_chlorophyll_a_in_sea_water status_flag"})

        self.attr_sigmat = MainAttr('sigmat',
            dtype= 'f4',
            atts={
                'standard_name' : 'sea_water_density',
                'long_name' : 'sea water density',
                'ncei_name': 'WATER DENSITY',
                'units' : 'kg/m^3',
                'valid_min': np.float32(0),
                'valid_max': np.float32(30)
            })
        self.attr_dVolt = MainAttr('diagnosticVoltage',
            dtype= 'f4',
            atts={
                # 'standard_name' : '', #???
                'long_name' : 'diagnostic voltage',
                'units' : 'V'
            })
        self.attr_cDr = MainAttr('currentDraw',
            dtype= 'f4',
            atts={
                # 'standard_name' : '', #???
                'long_name' : 'current draw',
                'units' : 'mA'
            })
        self.attr_a1 = MainAttr('aux1',
            dtype= 'f4',
            atts={
                'long_name' : 'Auxiliary 1',
                'units' : 'V',
            })
        self.attr_a3 = MainAttr('aux3',
            dtype= 'f4',
            atts={
                'long_name' : 'Auxiliary 3',
                'units' : 'V',
            })
        self.attr_a4 = MainAttr('aux4',
            dtype= 'f4',
            atts={
                'long_name' : 'Auxiliary 4',
                'units' : 'V',
            })


        self.attr_o2th= MainAttr('O2thermistor',
            dtype= 'f4',
            atts={
                # 'standard_name' : '', #???
                'long_name' : 'O2 thermistor', #???
                'units' : 'V', #not psu??
                # 'ncei_name': '',#??? 'OXYGEN', 'DISSOLVED OXYGEN', ...
                'instrument' : "instrument3",
                'platform': "platform1"
            }
            #qc
        )
        self.attr_o2thF1 = FlagAttr('O2thermistor_flagPrimary',
            atts={
                'long_name' : ', qc primary flag',
                # 'standard_name' : 'status_flag'
            })
        self.attr_o2thF2 = FlagAttr('O2thermistor_flagSecondary',
            atts={
                'long_name' : ', qc secondary flag',
                # 'standard_name' : 'status_flag'
            })
        self.attr_convOxy= MainAttr('convertedOxygen',
            dtype= 'f4',
            atts={
                'standard_name' : 'mass_concentration_of_oxygen_in_sea_water',
                'long_name' : 'converted_oxygen', #'dissolved oxygen (raw)'???
                'units' : 'mL/L',
                'instrument' : "instrument3",
                'platform': "platform1"
            }
            #qc
        )
        self.attr_convOxyF1 = FlagAttr('converted_oxygen_flagPrimary',
            atts={
                'long_name' : ', qc primary flag',
                'standard_name' : 'mass_concentration_of_oxygen_in_sea_water status_flag'
            })
        self.attr_convOxyF2 = FlagAttr('converted_oxygen_flagSecondary',
            atts={
                'long_name' : ', qc secondary flag',
                'standard_name' : 'mass_concentration_of_oxygen_in_sea_water status_flag'
            })

        # = MainAttr('',
        #     dtype= 'f4',
        #     atts={
        #
        #     }
        #     #qc
        # )
        # F = FlagAttr('',
        #     atts={})
        # F = FlagAttr('',
        #     atts={})

        #Instruments
        self.ch_i1 = CharVariable('instrument1', sta,
            atts={
                'make_model' : "Seabird SBE 16plus SEACAT",
                'long_name': 'SBE 16plus SEACAT',
                'ncei_name': 'CTD',
                'comment' : "Seabird SBE 16plus SEACAT Conductivity, Temperature," + \
                " and Pressure recorder. Derived output Salinity.",
                'ioos_code' : "urn:ioos:sensor:sccoos:"+self.sta.code_name+":conductivity_temperature_pressure"
            })
        self.ch_i2 = CharVariable('instrument2', sta,
            atts={
                'make_model' : "Seapoint Chlorophyll Fluorometer",
                'long_name': 'Chlorophyll Fluorometer',
                # 'ncei_name': '', ???
                'comment' : "Seapoint Chlorophyll Fluorometer with a 0-50 ug/L gain setting.",
                'ioos_code' : "urn:ioos:sensor:sccoos:"+self.sta.code_name+":chlorophyll"
            })
        self.ch_i3 = CharVariable('instrument3', sta,
            atts={
                'make_model' : "Seabird SBE 63 Optical Dissolved Oxygen (DO) Sensor",
                'long_name': "SBE 63 Optical Dissolved Oxygen (DO) Sensor",
                # 'comment' : "",
                # 'ncei_name': '', ???
                'ioos_code' : "urn:ioos:sensor:sccoos:"+self.sta.code_name+":oxygen"
            })

        platformDict = {
            'long_name' : self.sta.long_name,
            'ioos_code': "urn:ioos:station:sccoos:"+self.sta.code_name
        }
        if self.sta.wmo:
            platformDict.update({'wmo_code': self.sta.wmo})
        self.ch_p1 = CharVariable('platform1', sta, atts=platformDict)

    def createVariableTimeDim(self, ncfile, tv):
        if '_flag' in tv.name:
            ncVar = ncfile.createVariable(tv.name, 'B', ('time'), zlib=True)
        else:
            ncVar = ncfile.createVariable(tv.name, tv.dtype, ('time'), zlib=True)

        ncVar.setncatts(tv.atts);
        if '_flag' in tv.name:
            if '_flagPrimary' in tv.name:
                ncVar.setncatts({
                    'flag_values': bytearray([1, 2, 3, 4, 9]), # 1UB, 2UB, 3UB, 4UB, 9UB ;
                    'flag_meanings':'GOOD_DATA UNKNOWN SUSPECT BAD_DATA MISSING',
                });
            else:
                ncVar.setncatts({
                    'flag_values': bytearray([0, 1, 2, 3]), # 1UB, 2UB, 3UB, 4UB, 9UB ;
                    'flag_meanings':'UNSPECIFIED RANGE FLAT_LINE SPIKE',
                });
            ncVar.setncatts({
                'source':'QC results',
                'comment': "Quality Control test are based on IOOS's Quality Control of Real-Time Ocean Data (QARTOD))",
                'references':'https://github.com/ioos/qartod'
            });
        elif tv.name != 'time':
            ncVar.setncatts({
                'source':'insitu observations',
                'cell_methods': 'time: point',
                'grid_mapping':'crs',
                'coordinates':'time lat lon depth',
                'references': "http://sccoos.org/data/autoss/, http://sccoos.org/about/dmac/"
            })
            ncVar.setncatts(self.qc_meta(tv.name, tv.qc))

    def createVariableCharNoDim(self, ncfile, v):
        """createVariable, type 'S1' a.k.a. 'c' -character"""
        ncVar = ncfile.createVariable(v.name, 'S1')
        ncVar.setncatts(v.atts);

    def createNCshell(self, ncName, ignore): #dpmt??
        """Create netCDF shell: set global attributes/metadata

        .. todo::
            - move to nc.py or sccoos.py??
        """
        print "SASS createNCshell", ncName
        ncfile = Dataset(ncName, 'w', format='NETCDF4')
        self.metaDict.update({
            'id': ncName.split('/')[-1].split('.')[0],
            'comment': 'The '+self.sta.long_name+' automated shore station operated' + \
            ' by ' + self.sta.inst + \
            ' is mounted at a nominal depth of '+ str(self.sta.depth) +' meters MLLW. The' + \
            ' instrument package includes a Seabird SBE 16plus SEACAT Conductivity,' + \
            ' Temperature, and Pressure recorder, and a Seapoint Chlorophyll Fluorometer' + \
            ' with a 0-50 ug/L gain setting.',
            'contributor_name': self.sta.abbr+'/SCCOOS, SCCOOS/IOOS/NOAA, SCCOOS',
            'creator_name': self.sta.inst,
            'creator_url': self.sta.url,
            "date_created": self.tupToISO(time.gmtime()), #time.ctime(time.time()),
            'geospatial_bounds_crs': 'EPSG:4326',
            'geospatial_bounds_vertical_crs': 'EPSG:5829',
            'geospatial_bounds': 'POINT('+ str(self.sta.lon)+' '+str(self.sta.lat)+')',
            "geospatial_lat_min": self.sta.lat,
            "geospatial_lat_max": self.sta.lat,
            "geospatial_lon_min": self.sta.lon,
            "geospatial_lon_max": self.sta.lon,
            "geospatial_vertical_min": self.sta.depth,
            "geospatial_vertical_max": self.sta.depth,
            "history": "Created: "+ self.tupToISO(time.gmtime()), #time.ctime(time.time()),
            "title":self.metaDict["project"]+": "+self.sta.long_name,
            })
        if self.sta.wmo:
            self.metaDict.update({'wmo_code': self.sta.wmo})
        ncfile.setncatts(self.metaDict)

        time_dim = ncfile.createDimension('time', None)
        name_dim = ncfile.createDimension('stationNameLength', size=25)

        self.createVariableTimeDim(ncfile, self.attr_time)
        for tv in self.attrObjArr:
            self.createVariableTimeDim(ncfile, tv)

        for v in self.otherArr:
            self.createVariableCharNoDim(ncfile, v)

        nm = ncfile.createVariable('station', 'S1', 'stationNameLength')
        # nm = ncfile.createVariable('station', 'S1')
        nm.setncatts({
            'long_name' : self.sta.long_name,
            'cf_role' : 'timeseries_id'})
        # nm[:len(self.sta.code_name)] = list(self.sta.code_name)
        nm[:len(self.sta.long_name)] = list(self.sta.long_name)

        lat = ncfile.createVariable('lat', 'f4')
        lat.setncatts(self.meta_lat) #from nc.py
        lat.setncatts({
            'data_max':np.float32(self.sta.lat),
            'data_min':np.float32(self.sta.lat),
            'valid_max':np.float32(self.sta.lat),
            'valid_mix':np.float32(self.sta.lat)
        })
        ncfile.variables['lat'][0] = self.sta.lat

        lon = ncfile.createVariable('lon', 'f4')
        lon.setncatts(self.meta_lon)
        lon.setncatts({
            'data_max':np.float32(self.sta.lon),
            'data_min':np.float32(self.sta.lon),
            'valid_max':np.float32(self.sta.lon),
            'valid_min':np.float32(self.sta.lon)

        })
        ncfile.variables['lon'][0] = self.sta.lon

        dep = ncfile.createVariable('depth', 'f4')
        dep.setncatts(self.meta_dep)
        dep.setncatts({
            'data_max':np.float32(self.sta.depth),
            'data_min':np.float32(self.sta.depth),
            'valid_max':np.float32(self.sta.depth),
            'valid_min':np.float32(self.sta.depth)
        })
        ncfile.variables['depth'][0] = self.sta.depth

        crs = ncfile.createVariable('crs', 'd')
        crs.setncatts({
            'grid_mapping_name' : "latitude_longitude",
            'longitude_of_prime_meridian' : 0.0,
            'epsg_code' : "EPSG:4326",
            'semi_major_axis' : 6378137.0,
            'inverse_flattening' : 298.257223563})

        ncfile.close()

    def get_cols(self, colsDict, serverdate):
        """
        .. todo: columns if multiple, could be better

        :param dict colsDict: a dictionary with date strings as keys, values as array of column names
        :param str serverdate: should be first serverdate, only used if ^ colsDict contains more than one key
        :returns: appropriate array of column names
        """
        if len(colsDict) == 1:
            key = colsDict.keys()[0]
            return colsDict[key]
        else:
            #Use first Serverdate in dataframe to set whole dataset to only one set of columns, fix better later!!!
            dates = colsDict.keys()
            dates.sort()
            firstServerdateDt = pd.to_datetime(serverdate)
            useKey = ''
            for colKey in dates:
                colDt = pd.to_datetime(colKey)
                if firstServerdateDt>=colDt: useKey = colKey
            return colsDict[useKey]
            #Check that the list is equal to # of columns?!!!

    def textReader(self, filename, extDict):
        print os.path.isfile(filename), filename
        df = pd.read_csv(filename, sep='^', header=None, prefix='X',error_bad_lines=False)
        # Split data into proper columns
        df = df.X0.str.extract(self.regex)
        # Drop any rows with NaN
        df = df.dropna()

        df.columns = self.get_cols(extDict["cols"], df.iloc[0,0])
        # Set date_time to pandas datetime format
        dateformat = "%d %b %Y %H:%M:%S"
        # to_datetime (utc=None) --default-- and True results are the same
        df['date_time'] = pd.to_datetime(df.date+' '+df.time, format=dateformat)
        # Make date_time an index
        df.set_index('date_time', inplace=True)
        # df.index = df.index.tz_localize('UTC') #not needed?
        # Drop columns that were merged
        df.drop('date', axis=1, inplace=True)
        df.drop('time', axis=1, inplace=True)

        #only look at IPs for station (strip out other ips)
        df = df[df['ip'].isin(self.sta.ips)]
        return df

    def calc_factorOffset1(self, x, input):
        """
        :param x: row,
        :param array input: {'factor': a, 'offset':b]
        :returns: x times Factor plus Offset
        """
        try:
            return x.chlorophyll_raw*input['scale']+input['offset']

        except:
            return None


    def doCalc(self, row, **kwargs):
        """
        :param object row: row, with columns as attributes
        :param dictionary calcsDict: dictionary containing
        :returns: output from calculation function
        """
        calcsDict = kwargs['calcsDict']
        # col = kwargs['col']
        func = calcsDict[row.calcDate]['function']
        input = calcsDict[row.calcDate]['input']
        return eval('self.'+func)(row, input=input)

    def printCalc(self, row, **kwargs):
        """This is just for testing, to check the function/input being used on a value"""
        calcsDict = kwargs['calcsDict']
        # col = kwargs['col']
        func = calcsDict[row.calcDate]['function']
        input = calcsDict[row.calcDate]['input']
        return func+"()"+str(row)+")"+str(input)

    #Basic
    def calculations(self, df, extDict):
        for col in df.columns:
            if col not in ['server_date', 'ip']:
                #ALL might not be float in the future?
                df.loc[:,col] = df.loc[:,col].astype(float)
                #Check if column name has calculations
        for calc in self.calcArr:
            df['calcDate'] = pd.Series(np.repeat(pd.NaT, len(df)), df.index)
            dates = extDict['calcs'][calc].keys()
            dates.sort()
            #loop through dates and set appropriate date
            for calcDtStr in dates:
                calcDt = pd.to_datetime(calcDtStr, format='%Y-%m-%dT%H:%M:%SZ') #format?
                df['calcDate'] = [calcDtStr if i >= calcDt else df['calcDate'][i] for i in df.index]
            # df.rename(columns={calc: calc+'_raw'}, inplace=True)
            df[calc] = df.apply(self.doCalc, axis=1, calcsDict=extDict['calcs'][calc])
            df.drop('calcDate', axis=1, inplace=True)
                # if col in extDict['calcs']:
                #     df['calcDate'] = pd.Series(np.repeat(pd.NaT, len(df)), df.index)
                #     dates = extDict['calcs'][col].keys()
                #     dates.sort()
                #     #loop through dates and set appropriate date
                #     for calcDtStr in dates:
                #         calcDt = pd.to_datetime(calcDtStr, format='%Y-%m-%dT%H:%M:%SZ') #format?
                #         # df.loc[:,'calcDate'] = [calcDtStr if i >= calcDt else df['calcDate'][i] for i in df.index]
                #         df['calcDate'] = [calcDtStr if i >= calcDt else df['calcDate'][i] for i in df.index]
                #     df.rename(columns={col: col+'_raw'}, inplace=True)
                #     df.loc[:,col] = df.apply(self.doCalc, axis=1, col=col+'_raw', calcsDict=extDict['calcs'][col])
                #     # df[col+'_calc'] = df.apply(self.doCalc, axis=1, col=col, calcsDict=extDict['calcs'][col])
                #     # df[col+'_calcStr'] = df.apply(self.printCalc, axis=1, col=col, calcsDict=extDict['calcs'][col])
                #     df.drop('calcDate', axis=1, inplace=True)
        return df

    def text2nc(self, filename):
        """#previously dataframe2nc
        - Uses Panda's ``read_csv``
        - Does a series of regular expressions (a.k.a. regex)
        - Uses QC methods from **sassqc**

        .. note: most recent rewrite
            - Moved reading to ``textReader``
            - Moved calc to ``calculations``
            - Doing QC on netcdf, not text file

        .. todo:
            - columns if multiple, could be better. If change of column names
                happens in a dataset, it only applies one set of column names
            - qc_test for gap in Time, others
            - rewrite nc.dataToNC for createNCshell?, not passing 'lookup'

        :param str filename: filename, including directory location
        :param str regex: regular expression used in pandas's read_csv/extract
        :param array? columns: columns should contain: 'date', 'time', 'ip'; 'server_date'?
        """

        jsonFn = os.path.join(self.codedir, 'sass_'+self.sta.code_name+'_archive.json')
        print os.path.isfile(jsonFn), jsonFn
        with open(jsonFn) as json_file:
            extDict = json.load(json_file)

        df = self.textReader(filename, extDict)

        #groupby year. Since newyear text file can contain data from last year.
        groupedYr = df.groupby(df.index.year)
        for yr in groupedYr.indices:
            # Check file size, nccopy to bring size down, replace original file
            grpYr = groupedYr.get_group(yr)
            ncfilename = self.prefix+ str(yr) + '.nc'
            ncfilepath = os.path.join(self.ncpath, ncfilename)

            if os.path.isfile(ncfilepath):
                # ncfile = Dataset(ncName, 'r', format='NETCDF4')
                ds = xr.open_dataset(ncfilepath)
                ncDF = ds.to_dataframe()
                ds.close()
                print 'init size:', len(ncDF.index), 'last recorded:', ncDF.index[-1]

                ## Add the following: remove any entries from the subset that already exist!!!!!!!
                # exist = grpYr.epoch.isin(ncDep.variables['time'][:]) #
                # grpYr['epochs'] = grpYr.index.values.astype('int64') // 10**9
                exist  = grpYr.index.isin(ncDF.index)
                # appDF = grpYr[~exist]
                appDF = grpYr.loc[~exist]
            else:
                ncfile = self.createNCshell(ncfilepath, '')
                # appDF = grpYr
                appDF = grpYr.loc[:]
                ncDF = pd.DataFrame({})

            print 'number of new:', len(appDF)
            if len(appDF) > 0: # else all times are already in nc
            # if len(df) > 0:
                #set dataframe types, do calculations
                appDF = self.calculations(appDF, extDict)
                df2 = ncDF.append(appDF)
                #Drop all flag columns (will be reset)
                # for v in df2:
                #     if '_flag' in v: df2.drop(v, axis=1, inplace=True)

                print 'appending to:', ncfilepath
                ncfile = Dataset(ncfilepath, 'a', format='NETCDF4')
                print 'time lens', len(ncfile.variables['time']), df2.index.shape
                ncfile.variables['time'][0:] = df2.index.values.astype('int64') // 10**9
                for a in self.attrObjArr:
                    ## if the attribute has ANY of the qc attributes, run it through qc_tests
                    ## Flag variables should be AFTER base variable

                    # for qcv in MainAttr.qc_vars:
                    #     if qcv in a.__dict__.keys() and getattr(a, qcv) is not None:
                    #         df2 = self.qc_tests(df2, a.name, miss_val=a.miss_val,
                    #             sensor_span=a.sensor_span, user_span=a.user_span, low_reps=a.low_reps,
                    #             high_reps=a.high_reps, eps=a.eps,
                    #             low_thresh=a.low_thresh, high_thresh=a.high_thresh)
                    #         break

                    if hasattr(a, 'qc') and a.qc is not None:
                        print a.name, a.qc
                        df2 = self.qc_tests_obj(df2, a)

                    # print 'sizes', a.name, len(ncfile.variables[a.name][:]), df2[a.name].shape
                    ncfile.variables[a.name][0:] = df2[a.name].values
                    self.attrMinMax(ncfile, a.name)
                self.NCtimeMeta(ncfile)
                ncfile.close()
                ncfile = Dataset(ncfilepath, 'r', format='NETCDF4')
                ncfile.close()
                self.fileSizeChecker(ncfilepath)
                print 'finished appending file'

    def text2nc_all(self, qryMn):
        """ For now pass '201' to do all years (2013-2017)
        .. todo: make qryMn default to all without parameter pass.
        :param str qryMn: if in folder name, do text2nc. i.e. '2017'"""
        mnArr = os.listdir(self.logsdir)
        mnArr.sort()
        for mn in mnArr:
            if qryMn in mn:
                mnpath = os.path.join(self.logsdir, mn)
                if os.path.isdir(mnpath):
                    filesArr = os.listdir(mnpath)
                    filesArr.sort()
                    for fn in filesArr:
                        startfld = time.time() # time each folder
                        filename = os.path.join(mnpath, fn)
                        #print "\n" + fn,
                        self.text2nc(filename)

    def text2nc_append(self):
        """SASS log files are organized by server date (when recorded)
        .. todo::
            - if no lastNC file, run text2nc_all()
            - re-write? With every run, the latest file will always be gone
            through (columns, calcs, qc), even if no new data will be appended
            (exist in nc.dataToNC)
        """
        looplimit = 100
        loopCount = 1
        lastNC = self.getLastNC(self.prefix)
        print 'lastNC:', lastNC
        latest = self.getLastDateNC(lastNC)
        LRdt = datetime.datetime.utcfromtimestamp(latest)
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
                return loopCount

    def editOldNC(self, fname, newDir):
        '''Go through netcdfs and copy all sensor values, but do QC.
        New files also have the new metadata
        .. todo: add Boolean parameter for doing/replacing QC
        '''
        print 'Using old nc:', fname

        # ncfile = Dataset(fname, 'r')
        # print self.sta.code_name, len(ncfile.variables['time'][:])
        # ncfile.close()

        # newName = fname.split('.')[0]+"_new.nc"
        newName = os.path.join(newDir, fname.split('/')[-1])
        print 'new File:', newName
        self.createNCshell(newName, '')
        print 'created:', os.path.isfile(newName), newName
        # df = pd.read_hdf(fname, mode='r')
        ds = xr.open_dataset(fname)
        # print ds.info()
        # print ds.indexes
        # print ds.data_vars
        df = ds.to_dataframe()
        timeNum = len(df.index)
        print 'length', timeNum

        ## Remove QC variables IF re-doing QC
        for v in df:
            if '_flag' in v: df.drop(v, axis=1, inplace=True)

        # Write to new NCs
        # self.dataToNC(newName, df, '')

        df['epochs'] = df.index.values.astype('int64') // 10**9
        ncfile = Dataset(newName, 'a', format='NETCDF4')
        ncfile.variables['time'][0:] = df['epochs'].values

        for a in self.attrObjArr:
            ## Do QC if it has QC parameters
            if hasattr(a, 'qc') and a.qc is not None:
                print 'QC:', a.name
                df = self.qc_tests_obj(df, a)
            ncfile.variables[a.name][0:] = df[a.name].values
            self.attrMinMax(ncfile, a.name)
        self.NCtimeMeta(ncfile)
        ncfile.close()
        print 'done', fname

    def editOldNCs(self, newDir):
        # self.ncpath = '/data/InSitu/SASS/'
        print 'editOldNCs', self.ncpath
        filesArr = os.listdir(self.ncpath)
        filesArr.sort()
        for fn in filesArr:
            regex = re.search(re.compile('^'+self.prefix+'(\d{4})\.nc'), fn)
            if regex:
            # if self.prefix in fn and ('005' not in fn) and ('d02' not in fn):
                filename = os.path.join(self.ncpath, fn)
                #print "\n" + fn,
                self.editOldNC(filename, newDir)
        # fn =  self.sta.code_name+'-2006.nc'
        # self.editOldNC(os.path.join(self.ncpath, fn))

class Attr(object):
    @abstractmethod
    def __init__(self, name):
        # super(Attr, self).__init__(name)
        # self. = kwargs['']
        self.name = name

class MainAttr(Attr):
    # qc_vars = ['miss_val','sensor_span','user_span','low_reps','high_reps',
    #         'eps','low_thresh','high_thresh']

    def __init__(self, name, **kwargs):
        super(MainAttr, self).__init__(name)
        # self.sensor_span = kwargs['sensor_span']
        allowed_keys = set(['dtype','atts', 'qc'])
        # initialize all allowed keys to false
        self.__dict__.update((key, None) for key in allowed_keys) #None or False?
        # and update the given keys by their given values
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)
        # self.atts.update({'coordinates' : 'time lat lon depth'}) #<-- Not for 'time'!!

        #???
        # # self.calc = kwargs['calc']
        # self.calcFun = kwargs['calc_func']
        # self.calcIn = kwargs['calc_input']

class FlagAttr(Attr):
    def __init__(self, name, atts):
        super(FlagAttr, self).__init__(name)
        self.atts = atts

class CharVariable(object):
    def __init__(self, name, sta, atts):
        self.name = name
        self.atts = atts

class Regex(object):
    re_Y = r'[1-2]\d{3}' # Year
    re_d = r'[0-3]\d' # Days in Month
    re_b = r'[A-S][a-u][b-y]' # Month as abbreviated name
    re_timex = r'[0-2]\d:[0-5]\d:[0-5]\d'

    re_time = r'('+re_timex+')'
    re_s = r'(?:,?#?\s+|,)' # delimiter: space with optional comma, optional pound; or comma alone
    re_serverdate = r'('+re_Y+r'-[0-1]\d-'+re_d+'T'+re_timex+'Z)' # server date
    re_ip = r'(\d{2,3}\.\d{2,3}\.\d{2,3}\.\d{1,3})' # ip address ending in ',# '
    re_attr = r'(-?\d+\.?\d*)' # attribute number with: optional decimal, optional negative
    re_date = '('+re_d+re_s+re_b+re_s+re_Y+')' # date with Mon spelled/abbreviated

    def concatRegex(self, num):
        '''consecutive attribute, separated by delimiter'''
        return Regex.re_s.join([Regex.re_attr]*num)

class SASS_Basic(SASS):
    def __init__(self, sta):
        super(SASS_Basic, self).__init__(sta)
        print "init SASS_Basic"
        self.logsdir = r'/data/InSitu/SASS/data/'
        self.ncPostName = ''
        self.prefix = self.sta.code_name + self.ncPostName+"-"
        print "ncPostName: ", self.ncPostName, '. prefix:', self.prefix

        self.metaDict.update({
            'summary':'Automated shore station with a suite of sensors that are' +\
            ' attached to piers along the nearshore California coast.' + \
            ' These automated sensors measure temperature, salinity, chlorophyll' + \
            ' and water level at frequent intervals in the nearshore coastal ocean.' +\
            ' This data can provide local and regional information on mixing and upwelling,' +\
            ' land run-off, and algal blooms.'
            }) #add keywords !!!

        # self.metaDict['keywords'] += self.metaDict['keywords']+', ' #Add keywords


       # NOT INCLUDING 'time'
        self.attrObjArr = [
            self.attr_temp, self.attr_con, self.attr_pres, self.attr_sal,
            self.attr_chl1, self.attr_chl2,
            # self.attr_chl2, # don't have chl_raw for old files (editOldNC)
            self.attr_tempF1, self.attr_tempF2,
            self.attr_conF1, self.attr_conF2,
            self.attr_presF1, self.attr_presF2,
            self.attr_salF1, self.attr_salF2,
            self.attr_chlF1, self.attr_chlF2,
            self.attr_sigmat, self.attr_dVolt, self.attr_cDr,
            self.attr_a1, self.attr_a3, self.attr_a4]

        self.otherArr = [ self.ch_i1, self.ch_i2, self.ch_p1 ]

        r = Regex()
        self.regex = r'^'+r.re_serverdate+r.re_s+r.re_ip+r.re_s+r.concatRegex(8)+r.re_s+r.re_date+r.re_s+r.re_time+r.re_s+r.concatRegex(3)+r'$'

    def local2utc(self, start, end, adjSecs):
        '''
        .. warning: Some stations had some data recorded in local time instead of UTC.
        This method adjusts those local time to UTC.

        >>> sass_oop.SASS_Basic(sass_oop.ucsb).local2utc('2009-05-14', '2009-07-02T13:05', 25200)
        # +7:00 (25200)
        >>> sass_oop.SASS_Basic(sass_oop.ucla).local2utc('2005-06-15', '2008-11-30', 28800)
        # +8:00
        '''
        self.ncpath = '/home/scheim/NCobj/timeShift'
        sDate = pd.Timestamp(start) # UTC
        eDate = pd.Timestamp(end)
        print sDate, eDate
        for yr in range(sDate.year, eDate.year+1):
            sEp = sDate.value // 10**9
            eEp = eDate.value // 10**9
            ncfilename = self.prefix+ str(yr) + '.nc'
            filepath = os.path.join(self.ncpath, ncfilename)
            print 'edit', filepath
            if (os.path.isfile(filepath)):
                ds = xr.open_dataset(filepath)
                df = ds.to_dataframe()
                ds.close()
                timeNum = len(df.index)
                print 'length', timeNum
                print df.index[0], type(df.index[0])
                df['epoch'] = df.index.astype(np.int64) // 10 ** 9
                # df['adjTime'] = [ i.tz_localize('America/Los_Angeles').tz_convert('UTC') if sDate <= i <= eDate else i for i in df.index]
                df['adjTime'] = [ i+adjSecs if sEp <= i <= eEp else i for i in df.epoch]
                # print df['adjTime']

                # Write new time to existing NC
                print type(df.index), type(df.adjTime)
                # df['epochs'] = pd.to_datetime(df.adjTime, utc=True).values.astype('int64') // 10**9
                ncfile = Dataset(filepath, 'a', format='NETCDF4')
                ncfile.variables['time'][0:] = df['adjTime'].values
                self.NCtimeMeta(ncfile)
                ncfile.close()
                print 'done', filepath

class SASS_NPd2(SASS):
    def __init__(self, sta):
        super(SASS_NPd2, self).__init__(sta)
        """Setting up SASS Newport Pier new sensor

        .. todo::
            - QCs parameters for: O2thermistor and convertedOxygen (then add flags back for these)
        """
        print "init SASS_NPd2"
        self.logsdir = r'/data/InSitu/SASS/raw_data/newport_pier/'
        self.ncPostName = '-d02'
        self.prefix = self.sta.code_name + self.ncPostName+"-"

        self.metaDict.update({
            'summary':'Automated shore station with a suite of sensors that are' +\
            ' attached to piers along the nearshore California coast.' + \
            ' These automated sensors measure temperature, salinity, chlorophyll, ph' + \
            ' and water level at frequent intervals in the nearshore coastal ocean.' +\
            ' This data can provide local and regional information on mixing and upwelling,' +\
            ' land run-off, and algal blooms.'
            }) #add keywords !!!

        # self.metaDict['keywords'] += self.metaDict['keywords']+', ' #Add Oxygen keywords

       # NOT INCLUDING 'time'
        self.attrObjArr = [
            self.attr_temp, self.attr_con, self.attr_pres, self.attr_sal,
            self.attr_chl1, self.attr_chl2,
            self.attr_o2th, self.attr_convOxy,
            self.attr_tempF1, self.attr_tempF2,
            self.attr_conF1, self.attr_conF2,
            self.attr_presF1, self.attr_presF2,
            self.attr_salF1, self.attr_salF2,
            self.attr_chlF1, self.attr_chlF2,
            # self.attr_o2thF1, self.attr_o2thF2,
            # self.attr_convOxyF1, self.attr_convOxyF2,
            self.attr_sigmat, self.attr_dVolt, self.attr_cDr]

        self.otherArr = [ self.ch_i1, self.ch_i2, self.ch_i3, self.ch_p1 ]

        r = Regex()
        self.regex = r'^'+r.re_serverdate+r.re_s+r.re_ip+r.re_s+r.concatRegex(7)+r.re_s+r.re_date+r.re_s+r.re_time+r.re_s+r.concatRegex(3)+r'$'


class SASS_pH(SASS):
    def __init__(self, sta):
        super(SASS_pH, self).__init__(sta)
        """Setting up SASS Newport Pier new sensor

        .. warning: datetime is obtained by the server date. Not ideal, but a hack,
        since instrument wasn't able to send this. If there's a problem the instrument
        may send backed data all at once, and there's no way of knowing when that data
        was collected, so NO rows with duplicated server dates will be saved to netCDF.

        .. todo::
            - QCs parameters for: O2thermistor and convertedOxygen (then add flags back for these)
        """
        print "init SASS_ph"
        self.logsdir = r'/data/InSitu/SASS/raw_data/newport_pier_ph/'
        self.ncPostName = '-'
        self.prefix = self.sta.code_name +self.ncPostName
        self.calcArr = ['temperature', 'ph']

        self.metaDict.update({
            'instrument':'Data was collected with _____ instruments.',
            # 'summary':'Automated shore station with a suite of sensors that are' +\
            # ' attached to piers along the nearshore California coast.' + \
            # ' These automated sensors measure temperature, salinity, chlorophyll, ph' + \
            # ' and water level at frequent intervals in the nearshore coastal ocean.' +\
            # ' This data can provide local and regional information on mixing and upwelling,' +\
            # ' land run-off, and algal blooms.'
            }) #add keywords !!!

        # self.metaDict['keywords'] += self.metaDict['keywords']+', ' #Add ph keywords

        self.attr_phCount = MainAttr('ph_counts',
            dtype= 'f4',
            atts={
                # 'standard_name' : '',
                'long_name' : 'ph counts',
                # 'units' : '',
                'instrument' : "instrument1"
            })
        self.attr_phVolt = MainAttr('ph_voltage',
            dtype= 'f4',
            atts={
                # 'standard_name' : '',
                'long_name' : 'ph voltage',
                # 'units' : '',
                'instrument' : "instrument1"
            })
        self.attr_phRaw = MainAttr('ph_raw',
            dtype= 'f4',
            atts={
                # 'standard_name' : '',
                'long_name' : 'ph raw',
                # 'units' : '',
                'instrument' : "instrument1"
            })
        self.attr_tempCount = MainAttr('temp_counts',
            dtype= 'f4',
            atts={
                # 'standard_name' : '',
                'long_name' : 'temp counts',
                # 'units' : '',
                'instrument' : "instrument1"
            })
        self.attr_temp = MainAttr('temperature',
            dtype= 'f4',
            atts={
                'standard_name' : 'sea_water_temperature',
                'long_name' : 'sea water temperature',
                'units' : 'celsius',
                'instrument' : "instrument1"
            })
        self.attr_thermVolt = MainAttr('thermistor_voltage',
            dtype= 'f4',
            atts={
                # 'standard_name' : '',
                'long_name' : 'thermistor voltage',
                # 'units' : '',
                'instrument' : "instrument1"
            })
        self.attr_thermRaw = MainAttr('thermistor_raw',
            dtype= 'f4',
            atts={
                # 'standard_name' : '',
                'long_name' : 'thermistor raw',
                # 'units' : '',
                'instrument' : "instrument1"
            })
        self.attr_ph = MainAttr('ph',
            dtype= 'f4',
            atts={
                # 'standard_name' : '',
                'long_name' : 'pH',
                # 'units' : '',
                'instrument' : "instrument1"
            })

        self.ch_i1 = CharVariable('instrument1', sta,
            atts={
                'make_model' : "",
                'long_name': "",
                'comment' : "Instrument for measuring pH",
                'ioos_code' : "urn:ioos:sensor:sccoos:"+self.sta.code_name+":ph"
            })

       # NOT INCLUDING 'time'
        self.attrObjArr = [
                self.attr_phCount, self.attr_phVolt, self.attr_phRaw,
                self.attr_tempCount, self.attr_thermVolt, self.attr_thermRaw,
                self.attr_temp, self.attr_ph
                ]

        self.otherArr = [ self.ch_p1, self.ch_i1 ] #add instrument

        r = Regex()
        self.regex = r'^'+r.re_serverdate+r.re_s+r.re_ip+r.re_s+r.concatRegex(7)+r'$'

    def textReader(self, filename, extDict):
        print os.path.isfile(filename), filename
        df = pd.read_csv(filename, sep='^', header=None, prefix='X',error_bad_lines=False)
        # Split data into proper columns
        df = df.X0.str.extract(self.regex)
        # Drop any rows with NaN
        df = df.dropna()

        df.columns = self.get_cols(extDict["cols"], df.iloc[0,0])
        # Set date_time to pandas datetime format
        # to_datetime (utc=None) --default-- and True results are the same
        df['date_time'] = pd.to_datetime(df.server_date, format='%Y-%m-%dT%H:%M:%SZ')
        # Don't keep any rows with identical date_time/server_date. See warning in class.
        df.drop_duplicates(subset='date_time', keep=False, inplace=True)
        # Make date_time an index
        df.set_index('date_time', inplace=True)
        # df.index = df.index.tz_localize('UTC') #not needed?
        return df

    def calc_temp(self, row, input):
        """
        :param object row: pandas dataframe row with column name as attributes
        :param dictionary input: dictionary containing the following
        :param float input['temp_slope']:
        :param float input['temp_intercept']:
        """

        try:
            return row.temp_counts*input['temp_slope']+input['temp_intercept']

        except:
            return None

    def calc_ph(self, row, input):
        """
        :param object row: pandas dataframe row with column name as attributes
        :param dictionary input: dictionary containing the following
        :param float input['pH_slope']:
        :param float input['pH_intercept']:
        :param float input['pH_intercept']:
        :param float input['E0']:
        :param float input['Ts']:
        :param float input['R']:
        :param float input['F']:
        """

        try:
            TempK = row.temperature+273.15
            E0t= input['E0'] - 0.001 * (TempK - input['Ts'])
            ST = input['R'] * TempK * math.log(10) / input['F']
            Vo = row.ph_counts * input['pH_slope'] + input['pH_intercept']
            pH = (Vo - E0t) / ST

            return pH

        except:
            return None

    # def doCalc(self, row, **kwargs):
    #     """
    #     :param object row: row, with columns as attributes
    #     :param dictionary calcsDict:
    #     :returns: output from calculation function
    #     """
    #     calcsDict = kwargs['calcsDict']
    #     # col = kwargs['col']
    #     func = calcsDict[row.calcDate]['function']
    #     input = calcsDict[row.calcDate]['input']
    #     return eval('self.'+func)(row, input=input)
    #
    # def calculations(self, df, extDict):
    #     """
    #     .. note: Separate from SASS_Basic because, calculations needed to be done in a
    #     specific order (temperature BEFORE ph).
    #     .. todo: See note^. Merge both calculations methods to single parent.
    #     Impliment order of calculations (JSON? "calc_order")
    #     """
    #     for col in df.columns:
    #         if col not in ['server_date', 'ip']:
    #             #ALL might not be float in the future?
    #             df.loc[:,col] = df.loc[:,col].astype(float)
    #             #Check if column name has calculations
    #     for calc in ['temperature', 'ph']: # temperature needs to be done beofre ph
    #         df['calcDate'] = pd.Series(np.repeat(pd.NaT, len(df)), df.index)
    #         dates = extDict['calcs'][calc].keys()
    #         dates.sort()
    #         #loop through dates and set appropriate date
    #         for calcDtStr in dates:
    #             calcDt = pd.to_datetime(calcDtStr, format='%Y-%m-%dT%H:%M:%SZ') #format?
    #             df['calcDate'] = [calcDtStr if i >= calcDt else df['calcDate'][i] for i in df.index]
    #         # df.rename(columns={col: col+'_raw'}, inplace=True)
    #         df[calc] = df.apply(self.doCalc, axis=1, calcsDict=extDict['calcs'][calc])
    #         df.drop('calcDate', axis=1, inplace=True)
    #     return df

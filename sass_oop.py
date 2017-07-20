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
import sassqc #, qc #transition sassqc to qc

class SASS(sccoos.SCCOOS):
    """Class for SCCOOS's Automated Shore Stations. Currently, log files and netCDFs"""
    #set SASS metadata
    @abstractmethod
    def __init__(self):
        """Setting up SASS

        .. todo::
            - Add creator_institution. 'inst' is creator_name (change?).
        """
        super(SASS, self).__init__()
        #print "init sass"
        self.codedir = '/data/InSitu/SASS/code/NCobj'
#        self.ncpath = '/data/InSitu/SASS/netcdfs/'
        self.ncpath = '/home/scheim/NCobj/SASS'
        self.crontab = True

        self.metaDict.update({
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
            'processing_level':'QA/QC have been performed'
            })

class Attr(object):
    @abstractmethod
    def __init__(self):
        super(Attr, self).__init__(name)
        # self. = kwargs['']
        self.name = name

class MainAttr(Attr):
    def __init__(self, name, **kwargs):
        super(MainAttr, self).__init__(name)
        # self.sensor_span = kwargs['sensor_span']
        allowed_keys = set(['dtype','atts',
            'sensor_span','user_span','low_reps','high_reps',
            'eps','low_thresh','high_thresh'])
        # initialize all allowed keys to false
        self.__dict__.update((key, False) for key in allowed_keys)
        # and update the given keys by their given values
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)
        # self.atts.update({'coordinates' : 'time lat lon depth'}) #<-- Not for 'time'

        #???
        # # self.calc = kwargs['calc']
        # self.calcFun = kwargs['calc_func']
        # self.calcIn = kwargs['calc_input']

class FlagAttr(Attr):
    def __init__(self, name, atts):
        super(FlagAttr, self).__init__(name, 'S1')
        self.atts = atts

class Datfile(object):
    re_Y = r'[1-2]\d{3}' # Year
    re_d = r'[0-3]\d' # Days in Month
    re_b = r'[A-S][a-u][b-y]' # Month as abbreviated name
    re_time = r'[0-2]\d:[0-5]\d:[0-5]\d'
    re_s = r'(?:,?#?\s+|,)' # delimiter: space with optional comma, optional pound; or comma alone
    re_serverdate = r'^('+re_Y+r'-[0-1]\d-'+re_d+'T'+re_time+'Z)' # server date
    re_ip = r'(\d{2,3}\.\d{2,3}\.\d{2,3}\.\d{2,3})' # ip address ending in ',# '
    re_attr = r'(-?\d+\.?\d*)' # attribute number with: optional decimal, optional negative
    re_date = '('+re_d+re_s+re_b+re_s+re_Y+')' # date with Mon spelled/abbreviated

    def __init__(self, regex, columns):
        self.regex = regex
        self.columns = columns

    def concatRegex(self, num):
        '''consecutive attribute, separated by delimiter'''
        re_s.join([re_attr]*num)

class Station(SASS):
    def __init__(self, **kwargs):
        super(Station, self).__init__()
        allowed_keys = set(['code_name','long_name','dpmt', 'lat','lon','depth',
            'abbr','url','institute','columns'])
        # initialize all allowed keys to false
        self.__dict__.update((key, False) for key in allowed_keys)
        # and update the given keys by their given values
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)

    def stationMeta(self):
        self.metaDict.update({
            'comment': 'The '+self.long_name+' automated shore station operated' + \
            ' by ' + self.institute + \
            ' is mounted at a nominal depth of '+ self.depth +' meters MLLW.'
            # ' The instrument package includes a Seabird SBE 16plus SEACAT Conductivity,' + \
            # ' Temperature, and Pressure recorder, and a Seapoint Chlorophyll Fluorometer' + \
            # ' with a 0-50 ug/L gain setting.',
            'contributor_name': self.abbr+'/SCCOOS, SCCOOS/IOOS/NOAA, SCCOOS',
            'creator_name': self.institute,
            'creator_url': self.url,
            # "date_created": self.tupToISO(time.gmtime()), #time.ctime(time.time()),
            "geospatial_lat_min": self.lat,
            "geospatial_lat_max": self.lat,
            "geospatial_lon_min": self.lon,
            "geospatial_lon_max": self.lon,
            "geospatial_vertical_min": self.depth,
            "geospatial_vertical_max": self.depth,
            # "history": "Created: "+ self.tupToISO(time.gmtime()), #time.ctime(time.time()),
            "title":metaDict["project"]+": "+self.long_name,
            # "title": self.long_name #TEMP
        })
        return dict

class SASS_Basic(SASS):
    def __init__(self):
        super(SASS_Basic, self).__init__()
        self.logsdir = r'/data/InSitu/SASS/data/'

        self.metaDict.update({
            'instrument':'Data was collected with Seabird and Seapoint instruments.',
            'summary':'Automated shore station with a suite of sensors that are' +\
            ' attached to piers along the nearshore California coast.' + \
            ' These automated sensors measure temperature, salinity, chlorophyll' + \
            ' and water level at frequent intervals in the nearshore coastal ocean.' +\
            ' This data can provide local and regional information on mixing and upwelling,' +\
            ' land run-off, and algal blooms.'
            })

        temp = MainAttr('temperature'
            dtype= 'f4',
            atts={
                'standard_name' : 'sea_water_temperature',
                'long_name' : 'sea water temperature',
                'units' : 'celsius',
                'coordinates' : 'time lat lon depth',
                'instrument' : "instrument1"
            }
        )
        sal = MainAttr('temperature'
            dtype= 'f4',
            atts={
                'standard_name' : 'sea_water_salinity',
                'long_name' : 'sea water salinity',
                'units' : '1e-3', #not psu??
                'coordinates' : 'time lat lon depth',
                'instrument' : "instrument1"
            }
        )
        uci = Station(
            code_name = 'newport_pier'
            long_name = 'Newport Pier'
            dpmt = 1
            lat= 33.6061,
            lon= -117.9311,
            depth= '2',
            abbr='UCI',
            url= 'http://uci.edu/',
            inst= 'University of California, Irvine')
        ucsd = Station(
            code_name = 'scripps_pier'
            long_name = 'Scripps Pier'
            dpmt = 1
            lat= 32.867,
            lon= -117.257,
            depth= '5',
            abbr='UCSD',
            url= 'http://sccoos.org/',
            inst= 'Southern California Coastal Ocean Observing System (SCCOOS) at Scripps Institution of Oceanography (SIO)'}}
        )

    class SASS_NPd2(SASS):
        def __init__(self):
            super(SASS_NPd2, self).__init__()
            self.logsdir = r'/data/InSitu/SASS/raw_data/'

            self.metaDict.update({
                'instrument':'Data was collected with Seabird, Seapoint, and _____ instruments.',
                'summary':'Automated shore station with a suite of sensors that are' +\
                ' attached to piers along the nearshore California coast.' + \
                ' These automated sensors measure temperature, salinity, chlorophyll, ph' + \
                ' and water level at frequent intervals in the nearshore coastal ocean.' +\
                ' This data can provide local and regional information on mixing and upwelling,' +\
                ' land run-off, and algal blooms.'
                })

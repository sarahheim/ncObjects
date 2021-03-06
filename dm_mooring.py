#
# Author Sarah Heim
# Date create: 2016
# Description: class/objects, inheriting NC/SASS classes.
#   This class is created for Del Mar's mooring dataset
#
import os, time, datetime, json
start = time.time()
import pandas as pd
import numpy as np
from netCDF4 import Dataset
# from abc import ABCMeta, abstractmethod
# json.dump writes to a file or file-like object, whereas json.dumps returns a string

import sccoos

#TEMP
import sys
# from guppy import hpy
# gup = hpy()

class Moor(sccoos.SCCOOS):
    """Class for SCCOOS's Del Mar's mooring. Currently, log files and netCDFs."""
    def __init__(self, dpmt):
        """Setting up Moor variables

        .. todo:
            - lat,lon,dep variables could be recorded. And/or valid_min/valid_max could be exact.
        """
        self.dpmt = dpmt

        super(Moor, self).__init__()
        print "init dm_mooring. start time: ", self.tupToISO(time.gmtime())
        # self.logsdir = r'/home/scheim/NCobj/delmar_moor/' # TEMP!!!!!
        # self.ncpath = '/home/scheim/NCobj/DM_Moor' # TEMP!!!!!
        # self.crontab = False # TEMP!!!!!

        self.logsdir = r'/data/InSitu/DelMar/data'
        self.ncpath = r'/data/InSitu/DelMar/netcdf'
        self.crontab = True
        self.codedir = r'/data/InSitu/DelMar/code/ncobjects'
        self.extsDictFn = os.path.join(self.codedir, r'delmar_mooring_extensions.json')
        print 'Deployment:', self.dpmt
        print "USING JSON", self.extsDictFn
        # self.txtFnPre = 'CAF_RTproc_' !!!!!
        self.ncFnPre = ''
        self.txtFnDatePattern = '%Y%m%d%H%M'
        self.attrArr = ['temperature', 'temperature_flagPrimary', 'temperature_flagSecondary',
        'salinity', 'salinity_flagPrimary', 'salinity_flagSecondary']
        # self.attrArr = ['temperature', 'salinity']

        self.staMeta = {
            '11': {
                'lat': 32.929,
                'lon': -117.3265
            },
            '12': {
                'lat': 32.93,
                'lon': -117.317
            }
        }

        self.metaDict.update({
            'title':'Mooring: Del Mar',
            'product_version': 'v1',
            'cdm_data_type':'Station',
            'contributor_name': 'Hydraulics Lab-SIO//SCCOOS/, SCCOOS/IOOS/NOAA, SCCOOS', #maintenance by Scripps Diving Locker
            'contributor_role': 'station operation, station funding, data management', #??
            'creator_email':'info@sccoos.org', #??
            'creator_name':'Scripps Institution of Oceanography (SIO)', #???
            'creator_institution':'Scripps Institution of Oceanography (SIO)',
            'creator_type':'person',
            'creator_url':'http://sccoos.org', #Hydro Lab url?
            'featureType':"timeSeriesProfile",
            'geospatial_bounds_crs': 'EPSG:4326',
            'geospatial_bounds_vertical_crs': 'EPSG:5829',
            'geospatial_bounds': 'POINT('+str(self.staMeta[self.dpmt]['lon'])+' '+str(self.staMeta[self.dpmt]['lat'])+')',
            "geospatial_lat_min": self.staMeta[self.dpmt]['lat'],
            "geospatial_lat_max": self.staMeta[self.dpmt]['lat'],
            "geospatial_lon_min": self.staMeta[self.dpmt]['lon'],
            "geospatial_lon_max": self.staMeta[self.dpmt]['lon'],
            'geospatial_lat_resolution':'2.77E-4',
            'geospatial_lon_resolution':'2.77E-4',
            'geospatial_vertical_resolution':'1',
            "geospatial_vertical_units": 'm',
            'geospatial_vertical_positive': 'down',
            'history':'initial deployment 4 naut. miles offshore La Jolla, Feb. 2005 - Nov. 2005.' + \
            ' First deployment at the Del Mar site, Feb. 2006 - Dec. 2007.' + \
            ' Second deployment Jan. 2008 - Aug. 2008.' + \
            ' Third deployment Aug. 2008 - Nov. 2009.' + \
            ' Fourth deployment Nov. 2009 - May. 2011.' + \
            ' Fifth deployment Jun. 2011 - May. 2012' + \
            ' Sixth deployment Jun. 2012 - May. 2013.' + \
            ' Seventh deployment Jun. 2013 - May. 2014.' + \
            ' Eighth deployment May 2014 - Apr. 2015.' + \
            ' Ninth deployment Jun. 2015 - Oct. 2015.' + \
            ' Tenth deployment Nov. 2015 - Apr. 2016.' + \
            ' Eleventh deployment since May 2016.',
            'institution': 'Southern California Coastal Ocean Observing System (SCCOOS)' + \
            ' at Scripps Institution of Oceanography (SIO)',
            'keywords':'EARTH SCIENCE, OCEANS, SALINITY/DENSITY, SALINITY, TEMPERATURE,',##!!!
            'metadata_link':'http://mooring.ucsd.edu/index.html?/projects/delmar/delmar_intro.html',
            'processing_level':'QA/QC has been performed.',
            'project':'Del Mar, Mooring',
            'references':'http://sccoos.org/data/, http://mooring.ucsd.edu/index.html?/projects/delmar/delmar_intro.html, https://scripps.ucsd.edu/hlab, https://github.com/ioos/qartod',
            'summary': 'From February 2006 on, a mooring with a surface buoy has been maintained at a location on the 100-m isobath approximately three miles off Del Mar, CA. Instrumentation on the buoy includes a suite of meteorological sensors, sensors for surface water temperature, salinity, oxygen concentration, fluorescence, nutrients and currents. Further sensors on the mooring wire extend the measurements down into the water column, and much of the data is telemetered to shore in real-time through a radio or cell phone link.' + \
            ' Originally, the platform was developed in collaboration with the Hydraulics Laboratory as a part of the Southern California Coastal Ocean Observing System (SCCOOS). It has since developed into a testbed for instrument development, like for the first GEOCE mooring deployed in August 2008 until November 2009.' + \
            ' The mooring is operational, delivering real-time data, and being serviced annually. Recent servicing trips were incorporated into a university class, where students of the marine sciences and engineering could get hands-on experience with instrumentation, ship operations, and data acquisition.'+ \
            ' at the Scripps Institution of Oceanography.',
            'comment':'Geospatial lat/lon are a single location. Mooring does have GPS coordinates that could be incorporated or looked up separately.',
            'geospatial_lat_resolution':'2.77E-4',
            'geospatial_lon_resolution':'2.77E-4',
            'geospatial_vertical_resolution':'1',

            'platform_vocabulary': 'GCMD Earth Science Keywords. Version 5.3.3',
            'platform': 'mooring with a surface buoy',
            'instrument_vocabulary': 'GCMD Earth Science Keywords. Version 5.3.3',
            'instrument':'Data was collected with Sea-Bird: MicroCAT and SeaCAT instruments.',
        })

        # self.depArr = [0,7.5,16,25,35,47.5,60,75,90] <-- used with groups
        #'SN' --> 'deployment'; m = meters;
        self.defaultQC = {
            'temp1':{
                'miss_val':None, 'sensor_span': (-5,35),
                'low_reps':3, 'high_reps':5, 'eps':0.0001,
                'low_thresh': None, 'high_thresh': None
            },
            'temp2':{
                'miss_val':None, 'sensor_span': (-5,45),
                'low_reps':3, 'high_reps':5, 'eps':0.0001,
                'low_thresh': None, 'high_thresh': None
            },
            'sal1':{
                'miss_val':None, 'sensor_span': (2,42),
                'low_reps':3, 'high_reps':5, 'eps':0.00004,
                'low_thresh': None, 'high_thresh': None
            }
        }
        self.instrDict = {
            '6109':{
                'meta': {'make':"Sea-Bird", 'model':"SBE 16plus-IM V2 SeaCAT C-T (P) Recorder with  Inductive Modem interface"},
                '11': {
                    'm': 1,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp1'].items()+[('user_span', (8,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,34))])
                    }
                },
                '12': {
                    'm': 1,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp1'].items()+[('user_span', (8,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,34))])
                    }
                }
            },
            '05259':{
                'meta': {'make':"Sea-Bird", 'model':"SBE 37-IM MicroCAT C-T (P) Recorder"},
                '11': {
                    'm': 8,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (8,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,34))])
                    }
                },
                '12': {
                    'm': 8,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (8,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,34))])
                    }
                }
            },
            '2751':{
                'meta': {'make':"Sea-Bird", 'model':"SBE 16plus SeaCAT C-T (P) Recorder"},
                '11': {
                    'm': 16,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp1'].items()+[('user_span', (8,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,34))])
                    }
                }
            },
            '05128':{
                'meta': {'make':"Sea-Bird",'model':"SBE 37-IM MicroCAT C-T (P) Recorder"},
                '12': {
                    'm': 18,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (8,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,34))])
                    }
                }
            },
            '05357':{
                'meta': {'make':"Sea-Bird",'model':"SBE 37-IM MicroCAT C-T (P) Recorder"},
                '11': {
                    'm': 25,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (5,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,35))])
                    }
                },
                '12': {
                    'm': 24,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (5,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,35))])
                    }
                }
            },
            '06432':{
                'meta': {'make':"Sea-Bird", 'model':"SBE 16plus-IM V2 SeaCAT C-T (P) Recorder with  Inductive Modem interface"},
                '11': {
                    'm': 35,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp1'].items()+[('user_span', (5,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,35))])
                    }
                },
                '12': {
                    'm': 35,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp1'].items()+[('user_span', (5,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,35))])
                    }
                }
            },
            '05358':{
                'meta': {'make':"Sea-Bird", 'model':"SBE 37-IM MicroCAT C-T (P) Recorder"},
                '11': {
                    'm': 48,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (5,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,35))])
                    }
                },
                '12': {
                    'm': 48,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (5,25))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (31,35))])
                    }
                }
            },
            '05949':{
                'meta': {'make':"Sea-Bird",'model':"SBE 37-IM MicroCAT C-T (P) Recorder"},
                '11': {
                    'm': 60,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (5,17))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (32,35))])
                    }
                },
                '12': {
                    'm': 60,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (5,17))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (32,35))])
                    }
                }
            },
            '06984':{
                'meta': {'make':"Sea-Bird", 'model':"SBE 37-IM MicroCAT C-T (P) Recorder"},
                '11': {
                    'm': 75,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (5,17))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (32,35))])
                    }
                },
                '12': {
                    'm': 75,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp2'].items()+[('user_span', (5,17))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (32,35))])
                    }
                }
            },
            '4401':{
                'meta': {'make':"Sea-Bird",'model':"SBE 16plus-IM V2 SeaCAT C-T (P) Recorder with  Inductive Modem interface"},
                '12': {
                    'm': 90,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp1'].items()+[('user_span', (5,15))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (32,35))])
                    }
                }
            },
            '4402':{
                'meta': {'make':"Sea-Bird",'model':"SBE 16plus-IM V2 SeaCAT C-T (P) Recorder with  Inductive Modem interface"},
                '11': {
                    'm': 90,
                    'qc':{
                        'temperature':dict(self.defaultQC['temp1'].items()+[('user_span', (5,15))]),
                        'salinity':dict(self.defaultQC['sal1'].items()+[('user_span', (32,35))])
                    }
                }
            }
        }
        self.filesDict = {
            '11' :{
                '002c.sc0': {
                    'hdr_cols': ['sn', 'temperature', 'conductivity', 'ign1', 'ign2', 'ign3', 'datetime_str', 'salinity'],
                    'instruments': ['6109'],
                    'reader': 1
                },
                '002c': {
                    'hdr_cols': ['sn', 'temperature', 'conductivity', 'pressure', 'date', 'time', 'ign1', 'salinity'],
                    'instruments': ['2751'],
                    'reader': 2
                },
                '002c.mc1': {
                    'hdr_cols': ['sn', 'temperature', 'conductivity', 'date', 'time', 'ign1', 'salinity'],
                    'instruments': ['05259','05357','05358','05949','06984'],
                    'reader': 2
                },
                '002c.sc1': {
                    'hdr_cols': ['sn', 'temperature', 'conductivity', 'ign1', 'ign2', 'day', 'mon', 'yr', 'time', 'ign3', 'salinity'],
                    'instruments': ['06432','4402'],
                    'reader': 3
                }

            }, '12': {
                '002c.sc0': {
                    'hdr_cols': ['sn', 'temperature', 'conductivity', 'ign1', 'ign2', 'ign3', 'datetime_str', 'dunno', 'salinity'],
                    'instruments': ['6109'],
                    'reader': 1
                },
                '002c.mc1': {
                    'hdr_cols': ['sn', 'temperature', 'conductivity', 'date', 'time', 'ign1', 'salinity'],
                    'instruments': ['05259', '05128', '05357','05358','05949','06984'],
                    'reader': 2
                },
                '002c.sc1': {
                    'hdr_cols': ['sn', 'temperature', 'conductivity', 'ign1', 'ign2', 'day', 'mon', 'yr', 'time', 'ign3', 'salinity'],
                    'instruments': ['06432','4401'], #check 4401
                    'reader': 3
                }
            }
        }

    def createNCshell(self, ncName, lookup):
        sn = lookup['sn']
        # dpmt = lookup['dpmt']
        #NOT using: 'pH_aux', 'O2', 'O2sat'
        print "CAF createNCshell"
        ncfile = Dataset(ncName, 'w', format='NETCDF4')
        self.metaDict.update({
            'id':ncName.split('/')[-1], #filename
            'date_created': self.tupToISO(time.gmtime()),
            "geospatial_vertical_min": self.instrDict[sn][self.dpmt]['m'],
            "geospatial_vertical_max": self.instrDict[sn][self.dpmt]['m']
        })
        ncfile.setncatts(self.metaDict)
        #Move to NC/SCCOOS class???
        flagPrim_flag_values = bytearray([1, 2, 3, 4, 9]) # 1UB, 2UB, 3UB, 4UB, 9UB ;
        flagPrim_flag_meanings = 'GOOD_DATA UNKNOWN SUSPECT BAD_DATA MISSING'
        flagSec_flag_values = bytearray([0, 1, 2, 3]) # 1UB, 2UB, 3UB, 4UB, 9UB ;
        flagSec_flag_meanings = 'UNSPECIFIED RANGE FLAT_LINE SPIKE'
        dup_varatts = {
            'source':'insitu observations',
            'cell_methods': 'time: point longitude: point latitude: point',
            'grid_mapping':'crs',
            'coordinates':'time lat lon depth',
            'platform':'platform1',
            'instrument':'instrument1'
        }
        dup_flagatts = {
            'source':'QC results',
            'comment': "Quality Control test are based on IOOS's Quality Control of Real-Time Ocean Data (QARTOD))"
        }

        # for dI, d in enumerate(self.depArr):
        # for m in self.depArr: #for ~~groups~~
        #     for i in self.instrDict:
        # a depth could change instruments
        # if self.instrDict[sn]['m'] == m:
        ncGrp = str(int(self.instrDict[sn][self.dpmt]['m']))+'m'#+str(self.instrDict[sn]['d'])+'d'
        #instrument variables are in the root group
        inst = ncfile.createVariable('instrument1', 'c')
        inst.setncatts(self.instrDict[sn]['meta'])
        # inst.setncatts({
        #     "comment": "serial number: "+str(sn), #What if this changes???
        #     "geospatial_vertical_min": self.instrDict[sn][self.dpmt]['m'],
        #     "geospatial_vertical_max": self.instrDict[sn][self.dpmt]['m'],
        # })

        # #Create group for each depth/deployment
        # dep = ncfile.createGroup(ncGrp)

        # Create Dimensions
        # unlimited axis (can be appended to).
        time_dim = ncfile.createDimension('time', None)

        #Create Variables
        time_var = ncfile.createVariable(
            'time', np.int32, ('time'), zlib=True)  # int64? Gives error
        time_var.setncatts({
            'axis':"T",
            'calendar':'julian',
            'comment':'also known as Epoch or Unix time',
            'long_name':'time',
            'standard_name':'time',
            'units':'seconds since 1970-01-01 00:00:00 UTC'})

        # test = dep.createVariable(
        #     'test', np.int32, ('time'), zlib=True)  # np.int32

        temperature = ncfile.createVariable('temperature', 'f4', ('time'), zlib=True)
        temperature.setncatts({
            'long_name':'sea water temperature',
            'standard_name':'sea_water_temperature',
            'units':'celsius',
            'instrument':'instrument1'})
        temperature.setncatts(self.qc_meta('temperature', self.instrDict[sn][self.dpmt]['qc']['temperature']))
        temperature.setncatts(dup_varatts)
        temperature_flagPrim = ncfile.createVariable(
            'temperature_flagPrimary', 'B', ('time'), zlib=True)
        temperature_flagPrim.setncatts({
            'long_name':'sea water temperature, qc primary flag',
            'standard_name':"sea_water_temperature status_flag",
            'flag_values':flagPrim_flag_values,
            'flag_meanings':flagPrim_flag_meanings})
        temperature_flagPrim.setncatts(dup_flagatts)
        temperature_flagSec = ncfile.createVariable(
            'temperature_flagSecondary', 'B', ('time'), zlib=True)
        temperature_flagSec.setncatts({
            'long_name': 'sea water temperature, qc secondary flag',
            'standard_name':"sea_water_temperature status_flag",
            'flag_values': flagSec_flag_values,
            'flag_meanings': flagSec_flag_meanings})
        temperature_flagSec.setncatts(dup_flagatts)

        salinity = ncfile.createVariable('salinity', 'f4', ('time'), zlib=True)
        salinity.setncatts({
            'standard_name':'sea_water_salinity',
            'long_name':'sea water salinity',
            'units':'psu',
            'instrument':'instrument1'})
        salinity.setncatts(self.qc_meta('salinity', self.instrDict[sn][self.dpmt]['qc']['salinity']))
        salinity.setncatts(dup_varatts)
        salinity_flagPrim = ncfile.createVariable(
            'salinity_flagPrimary', 'B', ('time'), zlib=True)
        salinity_flagPrim.setncatts({
            'long_name':'sea water salinity, qc primary flag',
            'standard_name':"sea_water_practical_salinity status_flag",
            'flag_values':flagPrim_flag_values,
            'flag_meanings':flagPrim_flag_meanings})
        salinity_flagPrim.setncatts(dup_flagatts)
        salinity_flagSec = ncfile.createVariable(
            'salinity_flagSecondary', 'B', ('time'), zlib=True)
        salinity_flagSec.setncatts({
            'long_name':'sea water salinity, qc secondary flag',
            'standard_name':"sea_water_practical_salinity status_flag",
            'flag_values':flagSec_flag_values,
            'flag_meanings':flagSec_flag_meanings})
        salinity_flagSec.setncatts(dup_flagatts)

        platform1 = ncfile.createVariable('platform', 'c')
        platform1.setncatts({
        'long_name':'CCE-2 Mooring',
        'comment': 'CCE-2 (California Current Ecosystem)',
        'ioos_code':"urn:ioos:sensor:sccoos:delmar" })

        #
        # self.addNCshell_SCCOOS(ncfile)
        lat = ncfile.createVariable('lat', 'f4')
        lat.setncatts(self.meta_lat)
        lat.setncatts({
            'data_max': np.float32(self.staMeta[self.dpmt]['lat']),
            'data_min': np.float32(self.staMeta[self.dpmt]['lat']),
            'valid_min': np.float32(self.staMeta[self.dpmt]['lat']),
            'valid_max': np.float32(self.staMeta[self.dpmt]['lat'])
        })
        ncfile.variables['lat'][0] = self.staMeta[self.dpmt]['lat']
        lon = ncfile.createVariable('lon', 'f4')
        lon.setncatts(self.meta_lon)
        lon.setncatts({
            'data_max': np.float32(self.staMeta[self.dpmt]['lon']),
            'data_min': np.float32(self.staMeta[self.dpmt]['lon']),
            'valid_min':np.float32(self.staMeta[self.dpmt]['lon']),
            'valid_max':np.float32(self.staMeta[self.dpmt]['lon'])
        })
        ncfile.variables['lon'][0] = self.staMeta[self.dpmt]['lon']

        dep = ncfile.createVariable('depth', 'f4')
        dep.setncatts(self.meta_dep)
        lat.setncatts({
            'data_max': np.float32(self.instrDict[sn][self.dpmt]['m']),
            'data_min': np.float32(self.instrDict[sn][self.dpmt]['m']),
            'valid_min':np.float32(self.instrDict[sn][self.dpmt]['m']),
            'valid_max':np.float32(self.instrDict[sn][self.dpmt]['m'])
        })
        ncfile.variables['depth'][0] = self.instrDict[sn][self.dpmt]['m']

        # return ncfile
        ncfile.close()

    def read_csv1(self, fn, col_names):
        # df = pd.read_csv(fn, names=col_names, header=0, index_col=False, dtype={'sn': str})
        # df = pd.read_csv(fn, names=col_names, comment='%', index_col=False, dtype={'sn': str})
        df = pd.read_csv(fn, names=col_names, comment='%', index_col=False,
            converters={'sn': str}, skipinitialspace=True) #engine='python'
        df['date_time'] = pd.to_datetime(df.datetime_str, utc=None)
        return df

    def read_csv2(self, fn, col_names):
        # df = pd.read_csv(fn, names=col_names, header=0, index_col=False, dtype={'sn': str})
        # df = pd.read_csv(fn, names=col_names, comment='%', index_col=False, dtype={'sn': str})
        df = pd.read_csv(fn, names=col_names, comment='%', index_col=False,
            converters={'sn': str}) #'temperature':np.float32, 'salinity':np.float32
        df['date_time'] = pd.to_datetime(df.date+' '+df.time, utc=None)
        return df

    def read_csv3(self, fn, col_names):
        #using python engine because of sep regex
        df = pd.read_csv(fn, index_col=False, names=col_names,
            sep=',?\s+', comment='%', engine='python', converters={'sn': str}) #engine='python'
        format = '%d%b%Y %H:%M:%S'
        df['date_time'] = pd.to_datetime(df.day.astype(str)+df.mon+df.yr.astype(str)+' '+df.time, utc=None, format=format)
        return df

    # def getExtDict(dpmt, fnEnd):
    #     with open(self.extsDictFn) as json_file:
    #         extDict = json.load(json_file)
    #     if (dpmt in extDict) and (fnEnd in extDict[dpmt]):
    #         return extsDict[dpmt][fnEnd]
    #     else:
    #         empty = {
    #             "latest_file": "",
    #             "latest_epoch": 0,
    #             "latest_file_size": 0
    #         }
    #         return empty

    def setExtDict(self, fnEnd, fnDict):
        """fnDict should contain 'latest_file', 'latest_epoch' and 'latest_file_size' """
        # extDict[fnEnd]['latest_file'] = filename
        # extDict[fnEnd]['latest_epoch'] = dfMaxEp
        # extDict[fnEnd]['latest_file_size'] = fnSz
        ## extDict[fnEnd]['latest_file_mod'] = fnMod
        with open(self.extsDictFn) as json_file:
            extDict = json.load(json_file)
        if self.dpmt not in extDict: extDict[self.dpmt] = {}
        extDict[self.dpmt][fnEnd] = fnDict
        with open(self.extsDictFn, 'w') as json_file:
            json.dump(extDict, json_file, indent=4)

    def logFilepath(self, fn):
        return os.path.join(self.logsdir, self.dpmt, fn)

    # ##Rewrote, edited for depthd
    # def dataToNC(self, ncName, md, subset, lookup):
    #     """Take dataframe and put in netCDF (new file or append).
    #     Assumes there's a 'time' variable in data/ncfile"""
    #     if not os.path.isfile(ncName):
    #         self.createNCshell(ncName, lookup)
    #     ncfile = Dataset(ncName, 'a', format='NETCDF4')
    #     # ncGrp = str(self.instrDict[sn]['m'])+'m'+str(self.instrDict[sn]['d'])+'d'
    #     # ncDep = ncfile.groups[ncGrp] #!
    #     ncDep = ncfile.groups[md]
    #     dLen = len(ncDep.variables['time'][:])
    #     exist = subset.epoch.isin(ncDep.variables['time'][:])
    #     # exist = subset.index.isin(timeDepArr.values)
    #     appDF = subset[-exist]
    #     # print md, 'EXIST before len:', len(subset), 'after:', len(appDF)
    #     ncDep.variables['time'][dLen:] = np.array(appDF.epoch)
    #     for attr in self.attrArr:
    #         # print '\tappending', attr
    #         ncDep.variables[attr][dLen:] = np.array(appDF[attr])
    #         self.attrMinMax(ncDep, attr)
    #     ncfile.close()


    def text2nc(self, filename):
        fnEnd = filename.split('.', 1)[-1]
        print 'text2nc', filename, fnEnd
        log = self.logFilepath(filename)
        fnSz = os.path.getsize(log)
        # with open(self.extsDictFn) as json_file:
        #     extDict = json.load(json_file)
        if (fnEnd in self.filesDict[self.dpmt]) and ('reader' in self.filesDict[self.dpmt][fnEnd]):
            fDict = self.filesDict[self.dpmt][fnEnd]
            reader = 'read_csv'+str(fDict['reader'])
            # print 'reader:', reader
            df = eval('self.'+reader)(log, fDict['hdr_cols'])
            df['sn'] = df['sn'].str.strip()
            df = df[['sn','date_time','temperature','salinity']]
            # df['epoch'] = df.date_time.astype(np.int64) // 10**9
            df = df.dropna()
            # print df.dtypes
            # print 'pre astype', df.dtypes
            # df['temperature'] = df['temperature'].astype(float) #'float32'
            # df['salinity'] = df['salinity'].astype(float)
            # print 'post astype', df.dtypes
            # print 'all shape',  df.shape
            snGrouped = df.groupby('sn')
            # del df
            # print "Grouped", snGrouped.indices #, json.dumps(snGrouped.indices)
            for sn in snGrouped.indices:
                # print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'
                # print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
                # print '*********************************************'
                # print 'Group sn:', repr(sn), '-', str(self.instrDict[sn]['m'])+'m'
                dfSn = snGrouped.get_group(sn)
                dfSn.set_index('date_time', inplace=True)
                for attr in self.instrDict[sn][self.dpmt]['qc']:
                    # print 'QCing', sn, attr
                    qcIn = self.instrDict[sn][self.dpmt]['qc'][attr]
                    # print 'QC input:', qcIn
                    dfSn = self.qc_tests(dfSn, attr,
                        sensor_span=qcIn['sensor_span'], user_span=qcIn['user_span'],
                        low_reps=qcIn['low_reps'], high_reps=qcIn['high_reps'], eps=qcIn['eps'],
                        low_thresh=qcIn['low_thresh'], high_thresh=qcIn['high_thresh'])
                # print dfSn.head(2)
                groupedYr = dfSn.groupby(dfSn.index.year)
                for grpYr in groupedYr.indices:
                    ncGrp = str(int(self.instrDict[sn][self.dpmt]['m']))+'m'#+str(self.instrDict[sn]['d'])+'d'
                    ncfilename = self.ncFnPre + ncGrp + '-' + str(grpYr) + '.nc'
                    ncFilepath = os.path.join(self.ncpath, ncfilename)
                    self.dataToNC(ncFilepath, groupedYr.get_group(grpYr), {'sn': sn}) #'dpmt':dpmt
                    # self.dataToNC(filepath, dfSn, sn)
                    # print 'pre fileSizeChecker'
                    self.fileSizeChecker(ncFilepath)
                    # print 'end for: grpYr', grpYr
                # print 'end for: sn', sn
            # del snGrouped
            # dfMax = df['epoch'].max()
            dfMax = df.date_time.max()
            # print 'df.empty:', df.empty, 'df date_time max:', type(dfMax), dfMax
            # dfMaxEp = 0 if np.isnan(dfMax) else dfMax.astype(np.int64) // 10**9
            dfMaxEp = 0 if df.empty else dfMax.value // 10**9
            fnDict = {}
            fnDict['latest_file'] = filename
            fnDict['latest_epoch'] = dfMaxEp
            fnDict['latest_file_size'] = fnSz
            self.setExtDict(fnEnd, fnDict)
            # extDict[fnEnd]['latest_file'] = filename
            # extDict[fnEnd]['latest_epoch'] = dfMaxEp
            # extDict[fnEnd]['latest_file_size'] = fnSz
            # # extDict[fnEnd]['latest_file_mod'] = fnMod
            # with open(self.extsDictFn, 'w') as json_file:
            #     json.dump(extDict, json_file, indent=4)

        else:
            print 'ignoring file:', filename

    def text2nc_all(self):
        """If starting with all new text files:
        CT1169100u_11691_20160515.002c.sc1 line 31 was a problem line. If taken out,
        the rest run smoothly. """
        start = time.time()
        #reset all the extensions' latest recorded meta for this deployment
        if os.path.isfile(self.extsDictFn):
            with open(self.extsDictFn) as json_file:
                extDict = json.load(json_file)
        else:
            print 'NO JSON FILE'
            extDict = {}
        extDict[self.dpmt] = {}
        for ext in self.filesDict[self.dpmt]:
            # self.setExtDict(self.dpmt, ext, empty)
            extDict[self.dpmt][ext] = {
                "latest_file": "",
                "latest_epoch": 0,
                "latest_file_size": 0
            }
        with open(self.extsDictFn, 'w') as json_file:
            json.dump(extDict, json_file, indent=4)
        print 'REWROTE json for deployment', self.dpmt

        filesArr = os.listdir(os.path.join(self.logsdir, self.dpmt))
        filesArr.sort()
        for fn in filesArr:
            self.text2nc(fn)
        print "DONE! ALL files. Runtime:", time.time()-start

#     def text2nc_append(self):
#         """ Written to look at each depth's NC file to get the last recorded.
#         But this may go back farther than desired if depth stops recording
#             0 6109 002c.sc0 (2017, 4, 16)
#
#             16 2751 002c (2016, 12, 7)
#
#             25 05357 002c.mc1 (2017, 4, 16)
#             47 05358 002c.mc1 (2017, 4, 16)
#             60 05949 002c.mc1 (2017, 4, 16)
#             75 06984 002c.mc1 (2017, 4, 16)
#               7 05259 002c.mc1 (2016, 12, 20)
#
#             35 06432 002c.sc1 (2016, 12, 20)
#             90   4402 002c.sc1 (2017, 3, 3)
# """
    #     latestDict = {}
    #     for d in self.depArr:
    #         ncD = str(int(d))
    #         dLastNC = self.getLastNC(self.ncFnPre + ncD +'m-')
    #         dLast = self.getLastDateNC(dLastNC)
    #         print d, dLastNC, os.path.isfile(dLastNC), dLast
    #         latestDict[ncD] = dLast
    #     print latestDict
    #     for d in latestDict:
    #         print "lookup", d
    #         for instr in self.instrDict:
    #             if str(int(self.instrDict[instr]['m'])) == d: break
    #         for ext in self.filesDict:
    #             if instr in self.filesDict[ext]['instruments']: break
    #         LRdt = datetime.datetime.utcfromtimestamp(latestDict[d])
    #         print d, instr, ext, LRdt.timetuple()[0:3]

    def text2nc_append(self):
        with open(self.extsDictFn) as json_file:
            extDict = json.load(json_file)
        print extDict
        loopFlag = 0
        todayStr = time.strftime('%Y%m%d',time.gmtime())
        print 'todayStr:', todayStr
        for ext in extDict[self.dpmt]:
            filename = extDict[self.dpmt][ext]['latest_file']
            log = self.logFilepath(filename)
            if os.path.isfile(log):
                # fnEnd = filename.split('.', 1)[-1]
                fnDate = filename.split('.', 1)[0].split('_')[-1]
                print 'filename date:', fnDate
                prevFnSz = extDict[self.dpmt][ext]['latest_file_size']
                nowFnSz = os.path.getsize(log)
                print 'last sizes', prevFnSz, nowFnSz
                # if the size of the last file recorded has changed, append it
                if (prevFnSz != nowFnSz): self.text2nc(filename)
                # if the last file
                if (fnDate != todayStr): loopFlag +=1
            else:
                loopFlag +=1

        #Only loop through directory if the flag counter > 0
        print 'flag', loopFlag
        if loopFlag > 0:
            #Opt 1
            filesArr = os.listdir(os.path.join(self.logsdir, self.dpmt))
            filesArr.sort()
            # loop through all the files
            for fn in filesArr:
                fnEnd = fn.split('.', 1)[-1]
                print fn, fnEnd
                if (fnEnd in self.filesDict[self.dpmt]):
                    with open(self.extsDictFn) as json_file:
                        extDict = json.load(json_file)
                    print 'fileDate:', fn.split('.', 1)[0].split('_')[-1]
                    fileDate = time.strptime(fn.split('.', 1)[0].split('_')[-1], '%Y%m%d')
                    lastFile = self.logFilepath(extDict[self.dpmt][fnEnd]['latest_file']) ##asuming dictionary contains filename & isfile
                    if os.path.isfile(lastFile):
                        print 'lastDate:', lastFile.split('.', 1)[0].split('_')[-1]
                        lastDate = time.strptime(lastFile.split('.', 1)[0].split('_')[-1], '%Y%m%d')
                        # if files are newer than last recorded
                        if fileDate > lastDate:
                            self.text2nc(fn)
                        # now = time.gmtime()
                    else:
                        self.text2nc(fn)

            #Opt 2
            #Or increment from latest_file/ if lates_file is before today
            #What if
        print "DONE! Appending"

# d = Moor()
# d.text2nc_append()
# print "Done!", time.asctime(),"Runtime:", time.time()-start

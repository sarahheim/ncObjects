#
# Author Sarah Heim
# Date create: 2016
# Description: class/objects, inheriting NC/SASS classes.
#   This class is created for Del Mar's mooring dataset
#
import os, time, datetime, json

import pandas as pd
import numpy as np
from netCDF4 import Dataset
# from abc import ABCMeta, abstractmethod

import sccoos

#TEMP
import sys
# from guppy import hpy
# gup = hpy()

class Moor(sccoos.SCCOOS):
    """Class for SCCOOS's Del Mar's mooring. Currently, log files and netCDFs."""
    def __init__(self):
        """Setting up Moor variables

        .. todo: add more metadata to metaDict

        .. warning::
            - inital creation
        """

        super(Moor, self).__init__()
        print "init moor. start time: ", self.tupToISO(time.gmtime())
        self.logsdir = r'/home/scheim/NCobj/delmar_moor' # TEMP!!!!!
        # self.ncpath = '/data/InSitu/Moor/netcdf'
        self.ncpath = '/home/scheim/NCobj/DM_Moor' # TEMP!!!!!
        self.extsDictFn = 'delmar_mooring_extensions.json'
        print "USING JSON", self.extsDictFn
        # self.txtFnPre = 'CAF_RTproc_' !!!!!
        self.ncFnPre = 'Moor-'
        self.crontab = False # TEMP!!!!!
        self.txtFnDatePattern = '%Y%m%d%H%M'
        self.attrArr = ['temperature', 'temperature_flagPrimary', 'temperature_flagSecondary',
        'salinity', 'salinity_flagPrimary', 'salinity_flagSecondary']
        # self.attrArr = ['temperature', 'salinity']

        self.staMeta = {
            # 'depth': ,!!!
            'lat': 0,
            'lon': 0,
            #lat lon createVariable?!!!
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
            # 'geospatial_bounds': 'POINT(', self.staMeta['lon'],' ',self.staMeta['lat'],')'
            # "geospatial_lat_min": self.staMeta['lat'],
            # "geospatial_lat_max": self.staMeta['lat'],
            # "geospatial_lon_min": self.staMeta['lon'],
            # "geospatial_lon_max": self.staMeta['lon'],
            # "geospatial_vertical_min": self.staMeta['depth'],
            # "geospatial_vertical_max": self.staMeta['depth'],
            "geospatial_vertical_units": 'm',
            'geospatial_vertical_positive': 'down',
            'history':'',
            'institution': 'Southern California Coastal Ocean Observing System (SCCOOS)' + \
            ' at Scripps Institution of Oceanography (SIO)',
            'keywords':'EARTH SCIENCE, OCEANS, SALINITY/DENSITY, SALINITY, TEMPERATURE,',##!!!
            'metadata_link':'http://mooring.ucsd.edu/index.html?/projects/delmar/delmar_intro.html',
            'reference':'http://mooring.ucsd.edu/index.html?/projects/delmar/delmar_intro.html',
            'processing_level':'temporary QA/QC has been performed.', ##!!!
            'project':'Del Mar, Mooring',
            'references':'http://www.sccoos.org/data/, http://mooring.ucsd.edu/index.html?/projects/delmar/delmar_intro.html, https://scripps.ucsd.edu/hlab, https://github.com/ioos/qartod',
            'summary': 'With funding from.. ' + \
            ' From February 2006 on, a mooring with a surface buoy has been maintained at a location on the 100-m isobath approximately three miles off Del Mar, CA. Instrumentation on the buoy includes a suite of meteorological sensors, sensors for surface water temperature, salinity, oxygen concentration, fluorescence, nutrients and currents. Further sensors on the mooring wire extend the measurements down into the water column, and much of the data is telemetered to shore in real-time through a radio or cell phone link.' + \
            ' Originally, the platform was developed in collaboration with the Hydraulics Laboratory as a part of the Southern California Coastal Ocean Observing System (SCCOOS). It has since developed into a testbed for instrument development, like for the first GEOCE mooring deployed in August 2008 until November 2009.' + \
            ' The mooring is operational, delivering real-time data, and being serviced annually. Recent servicing trips were incorporated into a university class, where students of the marine sciences and engineering could get hands-on experience with instrumentation, ship operations, and data acquisition.'+ \
            ' at the Scripps Institution of Oceanography.',
            'comment':'qc parameters are placeholders. general values used for testing',
            # 'geospatial_lat_resolution':'',  # ?
            # 'geospatial_lon_resolution':'',  # ?
            # 'geospatial_vertical_resolution':'',  # ???

                'platform_vocabulary': 'GCMD Earth Science Keywords. Version 5.3.3',
                'platform': '', #???
                'instrument_vocabulary': 'GCMD Earth Science Keywords. Version 5.3.3',
                'instrument': 'Earth Science > Oceans > Ocean Temperature > Water Temperature, Earth Science > Oceans > Salinity/Density > Salinity,',
        })

        self.depArr = [0,7.5,16,25,35,47.5,60,75,90]
        #m = meters; d = deployment for depth
        self.instrDict = {
            '6109':{
                'm': 0,
                'd': 1,
                'meta': {'make':"Sea-Bird", 'model':"SBE 16plus SeaCAT"},
                'qc':{
                    'temperature':{
                        'miss_val':None,
                        'sensor_span': (-5,35), 'user_span': (12,27),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh': 1, 'high_thresh': 2
                    },
                    'salinity':{
                        'miss_val':None,
                        'sensor_span': (2,42), 'user_span': (30, 35),
                        'low_reps':3, 'high_reps':5, 'eps':0.00004,
                        'low_thresh': 0.4, 'high_thresh': 1.5
                    }
                }
            },
            '05259':{
                'm': 7.5,
                'd': 1,
                'meta': {'make':"Sea-Bird", 'model':"SBE 37 MicroCAT"},
                'qc':{
                    'temperature':{
                        'miss_val':None,
                        'sensor_span': (-5,45), 'user_span': (15,26),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh': 2, 'high_thresh': 4
                    },
                    'salinity':{
                        'miss_val':None,
                        'sensor_span': None, 'user_span': (30,35),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh': 0.5, 'high_thresh': 1.5
                    }
                }
            },
            '2751':{
                'm': 16,
                'd': 1,
                'meta': {'make':"Sea-Bird", 'model':"SBE 16 SeaCat"},
                'qc':{
                    'temperature':{
                        'miss_val':None,
                        'sensor_span': (-5,35), 'user_span': (10,20),
                        'low_reps':3, 'high_reps':5, 'eps':0.001,
                        'low_thresh':1.5, 'high_thresh': 3
                    },
                    'salinity':{
                        'miss_val':None,
                        'sensor_span': None, 'user_span': (30,35),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh': 0.4, 'high_thresh': 1
                    },
                }
            },
            '05357':{
                'm': 25,
                'd': 1,
                'meta': {'make':"Sea-Bird",'model':"SBE 37 MicroCAT"},
                'qc':{
                    'temperature':{
                        'miss_val':None,
                        'sensor_span': (-5,45), 'user_span': (10,16),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh': 2, 'high_thresh': 4
                    },
                    'salinity':{
                        'miss_val':None,
                        'sensor_span': None, 'user_span': (30,35),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh': 0.4, 'high_thresh': 1
                    }
                }
            },
            '06432':{
                'm': 35,
                'd': 1,
                'meta': {'make':"Sea-Bird", 'model':"SBE 16plus SeaCAT"},
                'qc':{
                    'temperature':{
                        'miss_val':None,
                        'sensor_span': (-5,35), 'user_span': (11,15),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh':0.6, 'high_thresh': 1.5
                    },
                    'salinity':{
                        'miss_val':None,
                        'sensor_span': (2,42), 'user_span': (30,35),
                        'low_reps':3, 'high_reps':5, 'eps':0.00004,
                        'low_thresh':0.5, 'high_thresh': 1.5
                    }
                }
            },
            '05358':{
                'm': 47.5,
                'd': 1,
                'meta': {'make':"Sea-Bird", 'model':"SBE 37 MicroCAT"},
                'qc':{
                    'temperature':{
                        'miss_val':None,
                        'sensor_span': (-5,45), 'user_span': (10,15),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh': 1, 'high_thresh': 3
                    },
                    'salinity':{
                        'miss_val':None,
                        'sensor_span': None, 'user_span': (30,35),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh': 0.5, 'high_thresh': 1.5
                    }
                }
            },
            '05949':{
                'm': 60,
                'd': 1,
                'meta': {'make':"Sea-Bird",'model':"SBE 37 MicroCAT"},
                'qc':{
                    'temperature':{
                        'miss_val':None,
                        'sensor_span': (-5,45), 'user_span': (8,14),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh':0.7, 'high_thresh': 3
                    },
                    'salinity':{
                        'miss_val':None,
                        'sensor_span': None, 'user_span': (30,35),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh':0.5,'high_thresh': 1
                    }
                }
            },
            '06984':{
                'm': 75,
                'd': 1,
                'meta': {'make':"Sea-Bird", 'model':"SBE 37 MicroCAT"},
                'qc':{
                    'temperature':{
                        'miss_val':None,
                        'sensor_span': (-5,45), 'user_span': (9,13),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh':0.7, 'high_thresh': 2
                    },
                    'salinity':{
                        'miss_val':None,
                        'sensor_span': None, 'user_span': (30,35),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh':0.5, 'high_thresh': 1
                    }
                }
            },
            '4402':{
                'm': 90,
                'd': 1,
                'meta': {'make':"Sea-Bird",'model':"SBE 16plus SeaCAT"},
                'qc':{
                    'temperature':{
                        'miss_val':None,
                        'sensor_span': (-5,35), 'user_span': (9,13),
                        'low_reps':3, 'high_reps':5, 'eps':0.0001,
                        'low_thresh':0.6, 'high_thresh': 1.5
                    },
                    'salinity':{
                        'miss_val':None,
                        'sensor_span': (2,42), 'user_span': (30,35),
                        'low_reps':3, 'high_reps':5, 'eps':0.00004,
                        'low_thresh':0.5, 'high_thresh': 1.5
                    }
                }
            }
        }
        self.filesDict = {
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
        }

    def createNCshell(self, ncName, sn):
        #NOT using: 'pH_aux', 'O2', 'O2sat'
        print "CAF createNCshell"
        ncfile = Dataset(ncName, 'w', format='NETCDF4')
        self.metaDict.update({
            'id':ncName.split('/')[-1], #filename
            'date_created': self.tupToISO(time.gmtime())
        })
        ncfile.setncatts(self.metaDict)
        #Move to NC/SCCOOS class???
        flagPrim_flag_values = bytearray([1, 2, 3, 4, 9]) # 1UB, 2UB, 3UB, 4UB, 9UB ;
        flagPrim_flag_meanings = 'GOOD_DATA UNKNOWN SUSPECT BAD_DATA MISSING'
        flagSec_flag_values = bytearray([0, 1, 2, 3]) # 1UB, 2UB, 3UB, 4UB, 9UB ;
        flagSec_flag_meanings = 'UNSPECIFIED RANGE FLAT_LINE SPIKE'
        dup_varatts = {
            'cell_methods': 'time: point longitude: point latitude: point',
            'source':'insitu observations',
            'grid_mapping':'crs',
            'coordinates':'time lat lon depth',
            'platform':'platform1',
            # 'instrument':'instrument1'
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
        ncGrp = str(int(self.instrDict[sn]['m']))+'m'+str(self.instrDict[sn]['d'])+'d'
        #instrument variables are in the root group
        inst = ncfile.createVariable('instrument'+ncGrp, 'i')
        inst.setncatts(self.instrDict[sn]['meta'])
        inst.setncatts({
            "geospatial_vertical_min": self.instrDict[sn]['m'],
            "geospatial_vertical_max": self.instrDict[sn]['m'],
        })

        # #Create group for each depth/deployment
        # dep = ncfile.createGroup(ncGrp)

        # Create Dimensions
        # unlimited axis (can be appended to).
        time_dim = ncfile.createDimension('time', None)


        # #Create Variables
        # dep = ncfile.createVariable('depth', 'f4', ('dep',), zlib=True)
        # dep.setncatts(self.meta_dep)
        # # dep[:] = self.depArr
        # lat.setncatts({
        #     'valid_min':self.staMeta['depth'],
        #     'valid_max':self.staMeta['depth']
        # })


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
            'instrument': 'instrument'+ncGrp})
        temperature.setncatts(self.qc_meta('temperature', self.instrDict[sn]['qc']['temperature']))
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
            'instrument': 'instrument'+ncGrp}) #?
        temperature.setncatts(self.qc_meta('salinity', self.instrDict[sn]['qc']['salinity']))
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

        platform1 = ncfile.createVariable('platform', 'i')
        platform1.setncatts({
        'long_name':'CCE-2 Mooring',
        'comment': 'CCE-2 (California Current Ecosystem)',
        'ioos_code':"urn:ioos:sensor:sccoos:delmar" })

        #
        # self.addNCshell_SCCOOS(ncfile)
        lat = ncfile.createVariable('lat', 'f4')
        lat.setncatts(self.meta_lat)
        lat.setncatts({
            'valid_min':self.staMeta['lat'],
            'valid_max':self.staMeta['lat']
        })
        ncfile.variables['lat'][0] = self.staMeta['lat']
        lon = ncfile.createVariable('lon', 'f4')
        lon.setncatts(self.meta_lon)
        lon.setncatts({
            'valid_min':self.staMeta['lon'],
            'valid_max':self.staMeta['lon']
        })
        ncfile.variables['lon'][0] = self.staMeta['lon']

        # return ncfile
        ncfile.close()

    def getLastDateNC(self, ncFilename, dep):
        """Re-written for mooring, since the latest time can vary per depth.
        Read a netCDF file and return the lastest time value in epoch/seconds

        :param str ncFilename: path of netCDF file
        :returns: latest time value in epoch/seconds
        :rtype: number (``float``), change to ``int``?

        """
        pass

    def read_csv1(self, fn, col_names):
        # df = pd.read_csv(fn, names=col_names, header=0, index_col=False, dtype={'sn': str})
        # df = pd.read_csv(fn, names=col_names, comment='%', index_col=False, dtype={'sn': str})
        df = pd.read_csv(fn, names=col_names, comment='%', index_col=False,
            engine='python', converters={'sn': str})
        df['date_time'] = pd.to_datetime(df.datetime_str, utc=None)
        return df

    def read_csv2(self, fn, col_names):
        # df = pd.read_csv(fn, names=col_names, header=0, index_col=False, dtype={'sn': str})
        # df = pd.read_csv(fn, names=col_names, comment='%', index_col=False, dtype={'sn': str})
        df = pd.read_csv(fn, names=col_names, comment='%', index_col=False,
            engine='python', converters={'sn': str}) #'temperature':np.float32, 'salinity':np.float32
        df['date_time'] = pd.to_datetime(df.date+' '+df.time, utc=None)
        return df

    def read_csv3(self, fn, col_names):
        #using python engine because of sep regex
        df = pd.read_csv(fn, index_col=False, names=col_names,
            sep=',?\s+', comment='%', engine='python', converters={'sn': str}) #engine='python'
        format = '%d%b%Y %H:%M:%S'
        df['date_time'] = pd.to_datetime(df.day.astype(str)+df.mon+df.yr.astype(str)+' '+df.time, utc=None, format=format)
        return df

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
        filepath = os.path.join(self.logsdir, filename)
        # fnMod = int(os.path.getmtime(filepath))
        fnSz = os.path.getsize(filepath)
        with open(self.extsDictFn) as json_file:
            extDict = json.load(json_file)
        # print 'is file:', os.path.isfile(filepath)
        # print "SIZE (1):", gup.heap().size
        if (fnEnd in self.filesDict) and ('reader' in self.filesDict[fnEnd]):
            fDict = self.filesDict[fnEnd]
            reader = 'read_csv'+str(fDict['reader'])
            print 'reader:', reader
            df = eval('self.'+reader)(filepath, fDict['hdr_cols'])
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
            depGrouped = df.groupby('sn')
            # del df
            # print "Grouped", depGrouped.indices #, json.dumps(depGrouped.indices)
            for dep in depGrouped.indices:
                # print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'
                # print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
                # print '*********************************************'
                # print 'Group dep:', repr(dep), '-', str(self.instrDict[dep]['m'])+'m'
                dfDep = depGrouped.get_group(dep)
                dfDep.set_index('date_time', inplace=True)
                # dfDep.set_index('epoch', inplace=True)
                # print 'dep shape', dfDep.shape
                # print dfDep.head(4)
                for attr in self.instrDict[dep]['qc']:
                    # print 'QCing', dep, attr
                    qcIn = self.instrDict[dep]['qc'][attr]
                    # print 'QC input:', qcIn
                    dfDep = self.qc_tests(dfDep, attr,
                        sensor_span=qcIn['sensor_span'], user_span=qcIn['user_span'],
                        low_reps=qcIn['low_reps'], high_reps=qcIn['high_reps'], eps=qcIn['eps'],
                        low_thresh=qcIn['low_thresh'], high_thresh=qcIn['high_thresh'])
                # print dfDep.head(2)
                groupedYr = dfDep.groupby(dfDep.index.year)
                for grpYr in groupedYr.indices:
                    ncGrp = str(int(self.instrDict[dep]['m']))+'m'+str(self.instrDict[dep]['d'])+'d'
                    ncfilename = self.ncFnPre + ncGrp + '-' + str(grpYr) + '.nc'
                    filepath = os.path.join(self.ncpath, ncfilename)
                    # self.dataToNC(filepath, groupedYr.get_group(grpYr), dep) # right??
                    self.dataToNC(filepath, dfDep, dep)
                    # print 'pre fileSizeChecker'
                    self.fileSizeChecker(filepath)
                    # print 'end for: grpYr', grpYr
                # print 'end for: dep', dep
            # del depGrouped
            # dfMax = df['epoch'].max()
            # dfMax = df.index.max()
            dfMax = (df.date_time.astype(np.int64) // 10**9).max()
            extDict[fnEnd]['latest_file'] = filename
            extDict[fnEnd]['latest_epoch'] = dfMax
            extDict[fnEnd]['latest_file_size'] = fnSz
            # extDict[fnEnd]['latest_file_mod'] = fnMod
            with open(self.extsDictFn, 'w') as json_file:
                json.dump(extDict, json_file, indent=4)
            print 'file done:', filename
            print '*********************************************'
        else:
            print 'ignoring file:', filename

    def text2nc_all(self):
        start = time.time()
        filesArr = os.listdir(self.logsdir)
        filesArr.sort()
        for fn in filesArr:
            self.text2nc(fn)
        print "DONE! ALL files. Runtime:", time.time()-start

    def text2nc_append(self):
        with open(self.extsDictFn) as json_file:
            extDict = json.load(json_file)
        print extDict
        loopFlag = 0
        todayStr = time.strftime('%Y%m%d',time.gmtime())
        print todayStr
        for ext in extDict:
            filename = extDict[ext]['latest_file']
            fnEnd = filename.split('.', 1)[-1]
            fnDate = filename.split('.', 1)[0].split('_')[-1]
            print 'filename date:', fnDate
            prevFnSz = extDict[ext]['latest_file_size']
            nowFnSz = os.path.getsize(os.path.join(os.path.join(self.logsdir, filename)))
            print 'last sizes', prevFnSz, nowFnSz
            # if the size of the last file recorded has changed, append it
            if (prevFnSz != nowFnSz): self.text2nc(filename)
            if (fnDate != todayStr): loopFlag +=1

        print 'flag', loopFlag
        if loopFlag > 0:
            #Opt 1
            filesArr = os.listdir(self.logsdir)
            filesArr.sort()
            for fn in filesArr:
                print fn
                fnEnd = fn.split('.', 1)[-1]
                print 'fnEnd:', fnEnd
                if (fnEnd in self.filesDict):
                    print 'fileDate:', fn.split('.', 1)[0].split('_')[-1]
                    fileDate = time.strptime(fn.split('.', 1)[0].split('_')[-1], '%Y%m%d')
                    lastFile = extDict[fnEnd]['latest_file'] ##asuming dictionary contains filename & isfile
                    print 'lastDate:', lastFile.split('.', 1)[0].split('_')[-1]
                    lastDate = time.strptime(lastFile.split('.', 1)[0].split('_')[-1], '%Y%m%d')
                    if fileDate > lastDate:
                        self.text2nc(fn)
                        with open(self.extsDictFn) as json_file:
                            extDict = json.load(json_file)
                    # now = time.gmtime()

            #Opt 2
            #Or increment from latest_file/ if lates_file is before today
            #What if
        print "DONE! Appending"

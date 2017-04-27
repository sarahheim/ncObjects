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
        self.logsdir = r'/home/scheim/NCobj/delmar_moor'
        # self.ncpath = '/data/InSitu/Moor/netcdf'
        self.ncpath = '/home/scheim/NCobj/DM_Moor'
        self.extsDictFn = 'delmar_mooring_extensions.json'
        # self.txtFnPre = 'CAF_RTproc_' !!!!!
        self.ncFnPre = 'Moor-'
        self.crontab = False
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
            'processing_level':'QA/QC has been performed', ##!!!
            'project':'Del Mar, Mooring',
            'references':'http://www.sccoos.org/data/, http://mooring.ucsd.edu/index.html?/projects/delmar/delmar_intro.html, https://scripps.ucsd.edu/hlab, https://github.com/ioos/qartod',
            'summary': 'With funding from.. ' + \
            ' From February 2006 on, a mooring with a surface buoy has been maintained at a location on the 100-m isobath approximately three miles off Del Mar, CA. Instrumentation on the buoy includes a suite of meteorological sensors, sensors for surface water temperature, salinity, oxygen concentration, fluorescence, nutrients and currents. Further sensors on the mooring wire extend the measurements down into the water column, and much of the data is telemetered to shore in real-time through a radio or cell phone link.' + \
            ' Originally, the platform was developed in collaboration with the Hydraulics Laboratory as a part of the Southern California Coastal Ocean Observing System (SCCOOS). It has since developed into a testbed for instrument development, like for the first GEOCE mooring deployed in August 2008 until November 2009.' + \
            ' The mooring is operational, delivering real-time data, and being serviced annually. Recent servicing trips were incorporated into a university class, where students of the marine sciences and engineering could get hands-on experience with instrumentation, ship operations, and data acquisition.'+ \
            ' at the Scripps Institution of Oceanography.',
            # 'comment':'', !!!
            # 'geospatial_lat_resolution':'',  # ?
            # 'geospatial_lon_resolution':'',  # ?
            # 'geospatial_vertical_resolution':'',  # ???

                'platform_vocabulary': 'GCMD Earth Science Keywords. Version 5.3.3',
                'platform': '', #???
                'instrument_vocabulary': 'GCMD Earth Science Keywords. Version 5.3.3',
                'instrument': 'Earth Science > Oceans > Ocean Temperature > Water Temperature, Earth Science > Oceans > Salinity/Density > Salinity,',
        })

        self.depArr = [0,7.5,16,25,35,47.5,60,75,90]
        self.filesDict = {
            '002c.sc0': {
                'hdr_cols': ['sn', 'temperature', 'conductivity', 'ign1', 'ign2', 'ign3', 'datetime_str', 'salinity'],
                'instrument':'Seacat',
                'depths':{
                    '6109': {'m':0,
                        'qc':{
                            'temperature':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (12,27),
                                'low_reps':3, 'high_reps':5, 'eps':0.0001,
                                'low_thresh': 1, 'high_thresh': 2
                            },
                            'salinity':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (30, 35),
                                'low_reps':3, 'high_reps':5, 'eps':0.0001,
                                'low_thresh': 0.4, 'high_thresh': 1.5
                            }
                        }
                }},
                'reader': 1
            },
            '002c': {
                'hdr_cols': ['sn', 'temperature', 'conductivity', 'pressure', 'date', 'time', 'ign1', 'salinity'],
                'instrument':'old seacat',
                # 'depths':{'2751':16},
                'depths':{
                    '2751': {'m':16,
                        'qc':{
                            'temperature':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (10,20),
                                'low_reps':3, 'high_reps':5, 'eps':0.0001,
                                'low_thresh':1.5, 'high_thresh': 3
                            },
                            'salinity':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (30,35),
                                'low_reps':3, 'high_reps':5, 'eps':0.0001,
                                'low_thresh': 0.4, 'high_thresh': 1
                            },
                        }
                }},
                'reader': 2
            },
            '002c.mc1': {
                'hdr_cols': ['sn', 'temperature', 'conductivity', 'date', 'time', 'ign1', 'salinity'],
                'instrument':'micro cat',
                'depths':{
                    '05259': {'m':7.5,
                        'qc':{
                            'temperature':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (15,26),
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
                    '05357': {'m': 25,
                        'qc':{
                            'temperature':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (10,16),
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
                    '05358': {'m':47.5,
                        'qc':{
                            'temperature':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (10,15),
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
                    '05949': {'m':60,
                        'qc':{
                            'temperature':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (8,14),
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
                    '06984': {'m':75,
                        'qc':{
                            'temperature':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (9,13),
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
                },
                'reader': 2
            },
            '002c.sc1': {
                'hdr_cols': ['sn', 'temperature', 'conductivity', 'ign1', 'ign2', 'day', 'mon', 'yr', 'time', 'ign3', 'salinity'],
                'instrument':'seacat',
                'depths':{
                    '06432': {'m':35,
                        'qc':{
                            'temperature':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (11,15),
                                'low_reps':3, 'high_reps':5, 'eps':0.0001,
                                'low_thresh':0.6, 'high_thresh': 1.5
                            },
                            'salinity':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (30,35),
                                'low_reps':3, 'high_reps':5, 'eps':0.0001,
                                'low_thresh':0.5, 'high_thresh': 1.5
                            }
                        }
                    },
                    '4402': {'m':90,
                        'qc':{
                            'temperature':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (9,13),
                                'low_reps':3, 'high_reps':5, 'eps':0.0001,
                                'low_thresh':0.6, 'high_thresh': 1.5
                            },
                            'salinity':{
                                'miss_val':None,
                                'sensor_span': None, 'user_span': (30,35),
                                'low_reps':3, 'high_reps':5, 'eps':0.0001,
                                'low_thresh':0.5, 'high_thresh': 1.5
                            }
                        }
                    },
                },
                'reader': 3
            }
        }

    def createNCshell(self, ncName, ignore):
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
            'instrument':'instrument1'
        }
        dup_flagatts = {
            'source':'QC results',
            'comment': "Quality Control test are based on IOOS's Quality Control of Real-Time Ocean Data (QARTOD))"
        }

        for d in self.depArr:
            #Create group for each depth
            dep = ncfile.createGroup(str(d))

            # Create Dimensions
            # unlimited axis (can be appended to).
            time_dim = dep.createDimension('time', None)


            # #Create Variables
            # dep = ncfile.createVariable('depth', 'f4', ('dep',), zlib=True)
            # dep.setncatts(self.meta_dep)
            # dep[:] = self.depArr
            # # lat.setncatts({
            # #     'valid_min':self.staMeta['depth'],
            # #     'valid_max':self.staMeta['depth']
            # # })


            time_var = dep.createVariable(
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

            temperature = dep.createVariable('temperature', 'f4', ('time'), zlib=True)
            temperature.setncatts({
                'long_name':'sea water temperature',
                'standard_name':'sea_water_temperature',
                'units':'celsius'})
            # temperature.setncatts(self.qc_meta['temperature'])
            temperature.setncatts(dup_varatts)
            temperature_flagPrim = dep.createVariable(
                'temperature_flagPrimary', 'B', ('time'), zlib=True)
            temperature_flagPrim.setncatts({
                'long_name':'sea water temperature, qc primary flag',
                'standard_name':"sea_water_temperature status_flag",
                'flag_values':flagPrim_flag_values,
                'flag_meanings':flagPrim_flag_meanings})
            temperature_flagPrim.setncatts(dup_flagatts)
            temperature_flagSec = dep.createVariable(
                'temperature_flagSecondary', 'B', ('time'), zlib=True)
            temperature_flagSec.setncatts({
                'long_name': 'sea water temperature, qc secondary flag',
                'standard_name':"sea_water_temperature status_flag",
                'flag_values': flagSec_flag_values,
                'flag_meanings': flagSec_flag_meanings})
            temperature_flagSec.setncatts(dup_flagatts)

            salinity = dep.createVariable('salinity', 'f4', ('time'), zlib=True)
            salinity.setncatts({
                'standard_name':'sea_water_salinity',
                'long_name':'sea water salinity',
                'units':'psu'}) #?
            # salinity.setncatts(self.qc_meta('salinity'))
            salinity.setncatts(dup_varatts)
            salinity_flagPrim = dep.createVariable(
                'salinity_flagPrimary', 'B', ('time'), zlib=True)
            salinity_flagPrim.setncatts({
                'long_name':'sea water salinity, qc primary flag',
                'standard_name':"sea_water_practical_salinity status_flag",
                'flag_values':flagPrim_flag_values,
                'flag_meanings':flagPrim_flag_meanings})
            salinity_flagPrim.setncatts(dup_flagatts)
            salinity_flagSec = dep.createVariable(
                'salinity_flagSecondary', 'B', ('time'), zlib=True)
            salinity_flagSec.setncatts({
                'long_name':'sea water salinity, qc secondary flag',
                'standard_name':"sea_water_practical_salinity status_flag",
                'flag_values':flagSec_flag_values,
                'flag_meanings':flagSec_flag_meanings})
            salinity_flagSec.setncatts(dup_flagatts)

        instrument1 = dep.createVariable('instrument1', 'i') #Licor??
        instrument1.setncatts({
            'make':"Sea-Bird",
            'model':"SBE 16 SeaCat",
            'comment':"" })
        instrument2 = dep.createVariable('instrument2', 'i') #Licor??
        instrument2.setncatts({
            'make':"Sea-Bird",
            'model':"SBE 16plus SeaCAT",
            'comment':"" })
        instrument3 = dep.createVariable('instrument3', 'i') #Licor??
        instrument3.setncatts({
            'make':"Sea-Bird",
            'model':"SBE 37 MicroCAT",
            'comment':"" })

        platform1 = dep.createVariable('platform', 'i')
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

    ##Rewrote, edited for depth
    def dataToNC(self, ncName, d, subset, lookup):
        """Take dataframe and put in netCDF (new file or append).
        Assumes there's a 'time' variable in data/ncfile"""
        if not os.path.isfile(ncName):
            self.createNCshell(ncName, lookup)
        ncfile = Dataset(ncName, 'a', format='NETCDF4')
        # timeDepArr = ncfile.variables['time'][dI]
        ncDep = ncfile.groups[str(d)]
        dLen = len(ncDep.variables['time'][:])

        exist = subset.epoch.isin(ncDep.variables['time'][:])
        # exist = subset.index.isin(timeDepArr.values)
        appDF = subset[-exist]
        print d, 'EXIST before len:', len(subset), 'after:', len(appDF)
        # appDF = subset
        # print d, "df len", len(subset), "appDF", len(appDF)
        # print 'add subset index', dI, 'LEN:', len(appDF), 'to:', dLen, type(timeDepArr)

        # ncfile.variables['time'][dI, y:] = np.array([appDF.index.astype('int64') // 10**9])
        ncDep.variables['time'][dLen:] = np.array(appDF.epoch)
        # ncfile.variables['test'][dI, y:] = np.array([np.arange(len(appDF.index))])
        # ncDep.variables['test'][dLen:] = np.array(appDF['test'])
        for attr in self.attrArr:
            # print '\tappending', attr
            ncDep.variables[attr][dLen:] = np.array(appDF[attr])
            # print "\tBEFORE: attr\n", ncfile.variables[attr][dI, :]
            # print 'DF', appDF[attr]
            # ncfile.variables[attr][dI, y:] = np.array([appDF[attr].astype(float)])
            # print 'types:', type(ncfile.variables[attr][dI][0]), type(appDF[attr][0])
            # ncfile.variables[attr][dI, y:] = np.array([appDF.temperature.astype('float32')])
            # ncfile.variables[attr][dI, y:] = np.array([appDF.temperature.astype(float)])
            # print "\tAFTER: attr\n", ncfile.variables[attr][dI, :]

            # print '\tappended', ncfile.variables[attr][dI]
        # print "POST APPEND:\n", ncDep.variables['time'][:]

        # print "CLOSED. SIZE (5):", gup.heap().size
        # print "POST array", ncfile.variables['time'][dI]
        # print 'pre NC CLOSE'
        ncfile.close()
        print 'post NC CLOSE'

        # if (dI == 7): #== 7 bad, 1 good
        #     print "CHECK and EXIT"
        #     print subset
        #     print
        #     ncfile = Dataset(ncName, 'r', format='NETCDF4')
        #     print ncfile.variables['time'][:]
        #     ncfile.close()
        #     sys.exit()
        # del ncfile


    def text2nc(self, filename):
        fnEnd = filename.split('.', 1)[-1]
        print filename, fnEnd
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
            df['epoch'] = df.date_time.astype(np.int64) // 10**9
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
                print '*********************************************'
                print 'Group dep:', repr(dep), '-', str(fDict['depths'][dep]['m'])+'m'
                dfDep = depGrouped.get_group(dep)
                dfDep.set_index('date_time', inplace=True)
                # print 'dep shape', dfDep.shape
                # print dfDep.head(4)
                for attr in fDict['depths'][dep]['qc']:
                    # print 'QCing', dep, attr
                    qcIn = fDict['depths'][dep]['qc'][attr]
                    # print 'QC input:', qcIn
                    dfDep = self.qc_tests(dfDep, attr,
                        sensor_span=qcIn['sensor_span'], user_span=qcIn['user_span'],
                        low_reps=qcIn['low_reps'], high_reps=qcIn['high_reps'], eps=qcIn['eps'],
                        low_thresh=qcIn['low_thresh'], high_thresh=qcIn['high_thresh'])
                # print dfDep.head(2)
                groupedYr = dfDep.groupby(dfDep.index.year)
                for grpYr in groupedYr.indices:
                    ncfilename = self.ncFnPre + str(grpYr) + '.nc'
                    filepath = os.path.join(self.ncpath, ncfilename)
                    self.dataToNC(filepath, fDict['depths'][dep]['m'], groupedYr.get_group(grpYr), '')
                    # print 'pre fileSizeChecker'
                    self.fileSizeChecker(filepath)
                    # print 'end for: grpYr', grpYr

                #!!! can drop sn in dfDep
                # print dfDep.head(2)
                # print 'end dep:', dep
                # print "SIZE (2):", gup.heap().size
                # del groupedYr, dfDep
                # print "SIZE (3):", gup.heap().size
                # print depGrp.describe()

                #!!! Rewrite getLastNC to look at depth dimension
                # lastNC = self.getLastNC('delmar_mooring-')
                # print "lastNC", lastNC
                print 'end for: dep', dep
            # del depGrouped
            dfMax = df['epoch'].max()
            extDict[fnEnd]['latest_file'] = filename
            extDict[fnEnd]['latest_epoch'] = dfMax
            extDict[fnEnd]['last_size'] = fnSz
            # extDict[fnEnd]['last_mod'] = fnMod
            with open(self.extsDictFn, 'w') as json_file:
                json.dump(extDict, json_file, indent=4)
            print 'file done:', filename
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
        #start with last recorded file
        #check if last_mod is diff
            #append
        #look for new files

        #if
        #Opt 1
        filesArr = os.listdir(self.logsdir)
        filesArr.sort()
        for fn in filesArr:
            print fn
            #if fn is newer? use modified date or date in name?
            #append

        #Opt 2
        #Or increment from latest_file/ if lates_file is before today
        #What if

print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
m = Moor()
print "ncpath", m.ncpath
print "logsdir", m.logsdir
# m.createNCshell('test.nc', '')
# m.text2nc('CT1169100u_11691_20160506.002c.mc1') #runs, but not correct
# m.text2nc('CT1169100u_11691_20160507.002c.mc1') #works
# m.text2nc('CT1169100u_11691_20160508.002c.mc1')
# m.text2nc('OS1169149u_11691_20160506_.002c')
# m.text2nc('OS1169149u_11691_20160506.002c')
# m.text2nc('')
m.text2nc_all()

#
# Author Sarah Heim
# Date create: 2016
# Description: adjusting to class/objects, inheriting NC classes.
# All datasets create object classes that will inherit this SCCOOS class
#

import os, re, time#, datetime

import pandas as pd
import numpy as np
from netCDF4 import Dataset
from abc import ABCMeta, abstractmethod

import nc, qc

class SCCOOS(nc.NC):
    """Class to be used for SCCOOS related netCDFs

    ..warning:: Assumptions: filename:prefix+YYYY.nc"""
    __metaclass__ = ABCMeta
    #add general SCCOOS metadata
    @abstractmethod
    def __init__(self):
        super(SCCOOS, self).__init__()
        #print "init sccoos"
        ##Meta
        self.metaDict.update({
            'acknowledgment':'The Southern California Coastal Ocean Observing System (SCCOOS)' + \
            ' is one of eleven regions that contribute to the national' + \
            ' U.S. Integrated Ocean Observing System (IOOS).',
            # 'contributor_name':'Southern California Coastal Ocean Observing System (SCCOOS)' + \
            # ' at Scripps Institution of Oceanography (SIO), NOAA, SCCOOS, IOOS',
            # 'creator_name':'Southern California Coastal Ocean Observing System (SCCOOS)' + \
            # ' at Scripps Institution of Oceanography (SIO)',
            # 'creator_url':'https://sccoos.org',
            'creator_email': 'info@sccoos.org',
            'institution': 'Scripps Institution of Oceanography, University of California San Diego',
            'publisher_institution': 'Scripps Institution of Oceanography (SIO)',
            'publisher_name':'Southern California Coastal Ocean Observing System',
            'publisher_type': 'position',
            'publisher_url':'http://sccoos.org',
            'publisher_email':'info@sccoos.org',
            'program': 'Southern California Coastal Ocean Observing System (SCCOOS)',
            'naming_authority':'sccoos.org',
            'source':'insitu observations',
            })

    def addNCshell_SCCOOS(self, ncfile):
        self.addNCshell_NC(ncfile)
       # print "addNCshell_SCCOOS"

    def getLastNC(self, prefix):
        """look at all nc file names and get last/latest year

        :param str prefix: filename prefix
        """
        ncFilesArr = os.listdir(self.ncpath)
        ncYrsArr = []
        for nc in ncFilesArr:
            if nc.startswith(prefix):
                ncYr = nc.split('.')[0].split('-')[-1]
                ncYrsArr.append(ncYr)
        ncYrsArr.sort()
        if len(ncYrsArr) > 0:
            return os.path.join(self.ncpath,prefix+ncYrsArr[-1]+'.nc')
        else:
            return None

        ##First assume lastest netCDF file is this year
        #thisYr = time.strftime('%Y')
        #lastNC = os.path.join(self.ncpath,prefix+thisYr+'.nc')
        ##If this year's nc file doesn't exist, get last year
        #if not os.path.isfile(lastNC):
        #    prevYr = str(int(thisYr)-1)
        #    lastNC = os.path.join(self.ncpath,prefix+prevYr+'.nc')
        #    ###Error if current or last year's nc's don't exist
        #    #if not os.path.isfile(lastNC):
        #return lastNC

    def getLastDateNC(self, ncFilename):
        """Read a netCDF file and return the lastest time value in epoch/seconds

        :param str ncFilename: path of netCDF file
        :returns: latest time value in epoch/seconds
        :rtype: number (``float``), change to ``int``?

        """
        if ncFilename is not None and os.path.isfile(ncFilename):
	# open netCDF file for reading.
            ncfile = Dataset(ncFilename,'r')
            # read the last unix timestamp in variable named 'time'.
            unixtime = ncfile.variables['time'][-1:][0]
            # close the NetCDF file
            ncfile.close()
        else:
            #unixtime = [1356998400] # 2013-01-01 00:00:00 UTC
            unixtime = 0
        #return pd.to_datetime(unixtime, unit='s', utc=None)[0].isoformat()
        return unixtime

    def getAttrOrKey(self, objDict, kat):
        """take specs and put into dictionary to be put in netcdf's variable's meta

        :param str kat: name of attribute or key
        :returns: meta

        """
        if hasattr(objDict, kat):
            return getattr(objDict, kat)
        elif (type(objDict) == dict) and (kat in objDict):
            return objDict[kat]
        else: return False

    def qc_meta(self, varName, qcSpecs):
        """take QC specs/parameters and put into dictionary to be put in netcdf's variable's meta

        :param str varName: name of variable
        :param qcSpecs: object or dictionary
        :returns: dictionary of meta

        """
        metaDict = {}
        comment = 'The following QC tests were done on '+varName+':'
        uspan = self.getAttrOrKey(qcSpecs, 'user_span')
        if uspan:
            comment += ' Range Check (Suspect): '+str(uspan)+';'

        sspan = self.getAttrOrKey(qcSpecs, 'sensor_span')
        if sspan:
            metaDict.update({
                'valid_min': np.float32(sspan[0]),
                'valid_max': np.float32(sspan[1])
            })
            comment += ' Range Check (Bad): '+str(sspan)+';'

        lreps = self.getAttrOrKey(qcSpecs, 'low_reps')
        hreps = self.getAttrOrKey(qcSpecs, 'high_reps')
        eps = self.getAttrOrKey(qcSpecs, 'eps')
        if (lreps) and (hreps) and (eps):
            comment += ' Flat Line Check (EPS): '+ str(eps)
            comment += ' (Suspect): '+ str(lreps)
            comment += ' (Bad): '+  str(hreps)+';'

        lthr = self.getAttrOrKey(qcSpecs, 'low_thresh')
        hthr = self.getAttrOrKey(qcSpecs, 'high_thresh')
        if (lthr) and (hthr):
            comment += ' Spike Test (Suspect): '+ str(lthr)
            comment += ' (Bad): '+ str(hthr)+';'

        if (comment == 'The following QC tests were done on '+varName+':'):
            comment += ' None.'
        metaDict.update({
            'comment': comment
        })
        return metaDict

    def qc_time_gap(self, dates1, dates2, allow):
        """ Check for gap in time between sensor time and recorded (server_date)
        .. warning: NOT done
        .. note: date arrays should be in pd.to_datetime

        Should flag be for QC on time only or variables

        :param dates1: The input array of observed values
        :param dates2: The input array of server time/recorded
        :param allow: cap in seconds
        :returns: An array of flagS
        """
        flag_arr = np.ones_like(dates1, dtype='uint8')
        time_gap = dates2-dates1

        # return flag_arr
        return time_gap #for testing

    def qc_time_interval(self, arr, interval):
        """ Check for gap in time array

        .. warning: NOT done

        Should flag be for QC on time only or variables
        :param arr: The input array of observed values
        :param interval: cap in seconds
        :returns: An array of flagS
        """
        flag_arr = np.ones_like(arr, dtype='uint8')

        #np.diff array is -1 size of original array
        diff = np.diff(arr)
        #insert a zero at the begining. array should now be same size as the data
        # print len(arr), len(diff)
        # print diff[0:5]
        diff = np.insert(diff, 0, 0)
        print len(arr), len(diff)
        print diff[0:5]
        flag_arr[:] = qc.QCFlags.GOOD_DATA
        flag_arr[(diff > interval)] = qc.QCFlags.SUSPECT

        flag_arr[0] = qc.QCFlags.UNKNOWN

        # return flag_arr
        return diff #for testing

    def qc_tests_obj(self, df, obj):
        """Run qc tests. NEW version of ``qc_tests``, which passes object,
        which can have various parameters

        .. warning: NEW version of ``qc_tests``

        .. todo::
            - add _FillValue attribute
            - add tests done to 'processing_level' metaDict
            - miss_val as input? change if statement(s)?... if parameter in obj.qc AND not None

        :param df: dataframe
        :param obj: object
        :param obj.name: object's name
        :param obj.qc: dictionary of qc parameters
        :returns: dataframe with primary and secondary flags added

        Expected kwargs: sensor_span, user_span"""
        # data = df[obj.name].values
        qc2flags = np.zeros_like(df[obj.name].values, dtype='uint8')

        # # Missing check
        # if obj.qc['miss_val']:
        # # if 'miss_val' in obj.qc:
        # # if obj.qc.get('miss_val'):
        #     qcflagsMiss = qc.check_nulls(df[obj.name].values)
        # else:
        #     qcflagsMiss = np.ones_like(df[obj.name].values, dtype='uint8')

        # Range Check
        # sensor_span = (-5,30)
        # user_span = (8,30)
        if obj.qc['sensor_span'] or obj.qc['user_span']:
            #because of OR
            sensor_span = obj.qc['sensor_span'] if 'sensor_span' in obj.qc else None
            user_span = obj.qc['user_span'] if 'user_span' in obj.qc else None
            qcflagsRange = qc.range_check(df[obj.name].values,sensor_span,user_span)
            qc2flags[(qcflagsRange > 2)] = 1 # Range
        else:
            qcflagsRange = np.ones_like(df[obj.name].values, dtype='uint8')

        # Flat Line Check
        # low_reps = 2
        # high_reps = 5
        # eps = 0.0001
        if obj.qc['low_reps'] and obj.qc['high_reps'] and obj.qc['eps']:
            qcflagsFlat = qc.flat_line_check(df[obj.name].values,obj.qc['low_reps'],obj.qc['high_reps'],obj.qc['eps'])
            qc2flags[(qcflagsFlat > 2)] = 2 # Flat line
        else:
            qcflagsFlat = np.ones_like(df[obj.name].values, dtype='uint8')

        # Spike Test
        # low_thresh = 2
        # high_thresh = 3
        if obj.qc['low_thresh'] and obj.qc['high_thresh']:
            # print obj.name, obj.qc['low_thresh'],obj.qc['high_thresh']
            qcflagsSpike = qc.spike_check(df[obj.name].values,obj.qc['low_thresh'],obj.qc['high_thresh'])
            qc2flags[(qcflagsSpike > 2)] = 3 # Spike
        else:
            qcflagsSpike = np.ones_like(df[obj.name].values, dtype='uint8')

        # if obj.qc['rec_time_col'] and obj.qc['delay']:
        #     print df.columns
        #     print obj.name, 'qc_time_gap', obj.qc['rec_time_col'], obj.qc['delay']
        #     # qcflagsTimeGap = self.qc_time_gap(pd.to_datetime(df[obj.qc['rec_time_col']].values),df.index.values,obj.qc['delay'])
        #     qcflagsTimeGap = self.qc_time_gap(pd.to_datetime(df.server_date.values),df.index.values,obj.qc['delay'])
        #     print qcflagsTimeGap
        #     # qc2flags[(qcflagsSpike > 2)] =  4# Time Gap
        # # else:
        # #     qcflagsTimeInvl = np.ones_like(df[obj.name].values, dtype='uint8')

        if 'time_interval' in obj.qc:
            print obj.name, 'qc_time_interval', obj.qc['time_interval']
            qcflagsTimeInvl = self.qc_time_interval(df[obj.name].values,obj.qc['time_interval'])
            print qcflagsTimeInvl
            # qc2flags[(qcflagsSpike > 2)] =  4# Time interval
        # else:
        #     qcflagsTimeInvl = np.ones_like(df[obj.name].values, dtype='uint8')

        # Find maximum qc flag
        # qcflags = np.maximum.reduce([qcflagsMiss, qcflagsRange, qcflagsFlat, qcflagsSpike])
        qcflags = np.maximum.reduce([qcflagsRange, qcflagsFlat, qcflagsSpike])
        # qcflags = np.maximum.reduce([qcflagsMiss, qcflagsRange, qcflagsFlat, qcflagsSpike, qcflagsGap, qcflagsTimeInvl])
        # print 'final primary flags:', obj.name,   qcflags[0:10]
        # print 'final secondary flags:',obj.name, qc2flags[0:10]

        # Output flags
        # print qcflags
        # print qc2flags
        # df.loc[:, (obj.name+'_flagPrimary')] = qcflags
        # df.loc[:, (obj.name+'_flagSecondary')] = qc2flags
        flags = pd.DataFrame({obj.name+'_flagPrimary':qcflags , obj.name+'_flagSecondary':qc2flags} , index=df.index)
        df = pd.concat([df, flags], axis=1)
        del qcflags, qc2flags
        # df.loc[:, obj.name+'_flagPrimary'] = pd.DataFrame(qcflags, index=df.index)
        # df.loc[:, obj.name+'_flagSecondary'] = pd.DataFrame(qc2flags, index=df.index)

        return df

    def qc_tests(self, df, attr, miss_val=None, sensor_span=None, user_span=None, low_reps=None,
    high_reps=None, eps=None, low_thresh=None, high_thresh=None):
        """Run qc tests. OLD version which passes various parameters

        .. warning: OLD version of ``qc_tests_obj``

        .. todo::
            - add _FillValue attribute

        .. todo: Change all children projects to use ``qc_tests_obj``

        :param df: dataframe
        :param attr: attribute, qa is being applied to
        :param boo miss_val: T/F; uses isnan
        :param sensor_span: for Range Test; tuple of low and high of good values (sensor)
        :param user_span: for Range Test; tuple of low and high of good values (expected/location appropriate)
        :param low_reps: for Flat Line check; number of repeating to be considered suspect
        :param high_reps: for Flat Line check; number of repeating to be considered bad
        :param eps: for Flat Line check;
        :param low_thresh: for Spike Test; see qc.spike_check
        :param high_thresh: for Spike Test; see qc.spike_check
        :returns: dataframe with primary and secondary flags added

        Expected kwargs: sensor_span, user_span"""
        # data = df[attr].values
        qc2flags = np.zeros_like(df[attr].values, dtype='uint8')

        # Missing check
        # if miss_val:
        if miss_val is not None:
            qcflagsMiss = qc.check_nulls(df[attr].values)
        else:
            qcflagsMiss = np.ones_like(df[attr].values, dtype='uint8')

        # Range Check
        # sensor_span = (-5,30)
        # user_span = (8,30)
        if sensor_span or user_span:
            qcflagsRange = qc.range_check(df[attr].values,sensor_span,user_span)
            qc2flags[(qcflagsRange > 2)] = 1 # Range
        else:
            qcflagsRange = np.ones_like(df[attr].values, dtype='uint8')

        # Flat Line Check
        # low_reps = 2
        # high_reps = 5
        # eps = 0.0001
        if low_reps and high_reps and eps:
            qcflagsFlat = qc.flat_line_check(df[attr].values,low_reps,high_reps,eps)
            qc2flags[(qcflagsFlat > 2)] = 2 # Flat line
        else:
            qcflagsFlat = np.ones_like(df[attr].values, dtype='uint8')

        # Spike Test
        # low_thresh = 2
        # high_thresh = 3
        if low_thresh and high_thresh:
            qcflagsSpike = qc.spike_check(df[attr].values,low_thresh,high_thresh)
            qc2flags[(qcflagsSpike > 2)] = 3 # Spike
        else:
            qcflagsSpike = np.ones_like(df[attr].values, dtype='uint8')

        # print 'all pre flags:', attr, data[0], type(data[0]), np.isnan(data[0]), qcflagsMiss[0], qcflagsRange[0], qcflagsFlat[0], qcflagsSpike[0]
        # Find maximum qc flag
        qcflags = np.maximum.reduce([qcflagsMiss, qcflagsRange, qcflagsFlat, qcflagsSpike])
        # print 'final primary flags:', attr,   qcflags[0:10]
        # print 'final secondary flags:',attr, qc2flags[0:10]

        # Output flags
        # print qcflags
        # print qc2flags
        # df.loc[:, (attr+'_flagPrimary')] = qcflags
        # df.loc[:, (attr+'_flagSecondary')] = qc2flags
        flags = pd.DataFrame({attr+'_flagPrimary':qcflags , attr+'_flagSecondary':qc2flags} , index=df.index)
        df = pd.concat([df, flags], axis=1)
        del qcflags, qc2flags
        # df.loc[:, attr+'_flagPrimary'] = pd.DataFrame(qcflags, index=df.index)
        # df.loc[:, attr+'_flagSecondary'] = pd.DataFrame(qc2flags, index=df.index)

        return df

    def flagStats_allYears(self, csvName):
        """Loop through all years/netCDFs make a CSV file of flag counts

        .. todo: make ``flagStats_single`` a required function/abstractmethod for all projects
        """
        start = time.time()
        print 'dfStats_allYears ncpath:', self.ncpath
        filesArr = os.listdir(self.ncpath)
        filesArr.sort()
        dict = {}
        for fn in filesArr:
            regex = re.search(re.compile('^'+self.prefix+'(\d{4})\.nc'), fn)
            if regex:
                yr = regex.group(1)
                print yr, fn
                dict[yr] = self.flagStats_single(os.path.join(self.ncpath, fn))
        pd.DataFrame(dict).to_csv(csvName)
        print "Done!", time.asctime(),"Runtime:", time.time()-start

    def runAllNCyrs(self, func):
        """Loop through all years/netCDFs and apply specified function

        :param str func: function name to be applied to all netCDFs
        """
        print 'runAllNCyrs ncpath:', self.ncpath
        filesArr = os.listdir(self.ncpath)
        filesArr.sort()
        for fn in filesArr:
            if re.search(re.compile('^'+self.prefix+'\d{4}\.nc'), fn):
                print 'function:', func, 'file:', fn
                eval(func)(os.path.join(self.ncpath, fn))

#print c.ncpath
#c.updateNCattrs_all()

#
# Author Sarah Heim
# Date create: 2016
# Description: adjusting to class/objects, inheriting NC classes.
# All datasets create object classes that will inherit this SCCOOS class
#

import os #, time, datetime

import pandas as pd
import numpy as np
from netCDF4 import Dataset
from abc import ABCMeta, abstractmethod

import nc, qc

class SCCOOS(nc.NC):
    """Class to be used for SCCOOS related netCDFs"""
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
        """look at all nc file names and get last year"""
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

    def qc_meta(self, attr):
        qcDict = {'references':'https://github.com/ioos/qartod'}
        comment = 'The following QC tests were done on '+attr+'.'
        if self.qc_values[attr]['user_span']:
            qcDict.update({
                'data_min': self.qc_values[attr]['user_span'][0],
                'data_max': self.qc_values[attr]['user_span'][1]
            })
            comment += ' Range Check - Suspect: '+str(self.qc_values[attr]['user_span'])

        if self.qc_values[attr]['sensor_span']:
            qcDict.update({
                'valid_min': self.qc_values[attr]['sensor_span'][0],
                'valid_max': self.qc_values[attr]['sensor_span'][1]
            })
            comment += ' Range Check - Bad: '+str(self.qc_values[attr]['sensor_span'])

        if self.qc_values[attr]['low_reps'] and self.qc_values[attr]['high_reps'] and self.qc_values[attr]['eps']:
            comment += ' Flat Line Check - EPS: '+ str(self.qc_values[attr]['eps'])
            comment += ' Flat Line Check - Suspect: '+ str(self.qc_values[attr]['low_thresh'])
            comment += ' Flat Line Check - Bad: '+  str(self.qc_values[attr]['high_thresh'])

        if self.qc_values[attr]['low_thresh'] and self.qc_values[attr]['high_thresh']:
            comment += ' Spike Test - Suspect: '+ str(self.qc_values[attr]['low_reps'])
            comment += ' Spike Test - Bad: '+ str(self.qc_values[attr]['high_reps'])

        qcDict.update({
            'comment': comment
        })
        return qcDict

    def qc_tests(self, df, attr, miss_val=None, sensor_span=None, user_span=None, low_reps=None,
    high_reps=None, eps=None, low_thresh=None, high_thresh=None):
        """Run qc

        .. todo::
            - add _FillValue attribute
            - add tests done to 'processing_level' metaDict
            - add qc input into metadata

        :param df: dataframe
        :param attr: attribute, qa is being applied to
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
        if miss_val is not None:
            qcflagsMiss = qc.check_nulls(df[attr].values)
            #nothing for secondary flag if missing?

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

#print c.ncpath
#c.updateNCattrs_all()

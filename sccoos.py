#
# Author Sarah Heim
# Date create: 2016
# Description: adjusting to class/objects, inheriting NC classes.
# All datasets create object classes that will inherit this SCCOOS class
#

import os #, time, datetime

# import pandas as pd
# import numpy as np
from netCDF4 import Dataset
from abc import ABCMeta, abstractmethod

import nc

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
            'creator_url':'https://sccoos.org',
            'creator_name':'Southern California Coastal Ocean Observing System (SCCOOS)' + \
            ' at Scripps Institution of Oceanography (SIO)',
            'contributor_name':'Southern California Coastal Ocean Observing System (SCCOOS)' + \
            ' at Scripps Institution of Oceanography (SIO), NOAA, SCCOOS, IOOS',
            'acknowledgment':'The Southern California Coastal Ocean Observing System (SCCOOS)' + \
            ' is one of eleven regions that contribute to the national ' + \
            'U.S. Integrated Ocean Observing System (IOOS).',
            'publisher_name':'Southern California Coastal Ocean Observing System',
            'publisher_url':'http://sccoos.org',
            'publisher_email':'info@sccoos.org',
            'naming_authority':'sccoos.org',
            'source':'insitu observations'
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


#print c.ncpath
#c.updateNCattrs_all()

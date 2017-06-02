#
# Author Sarah Heim
# Date create: 2016
# Description: adjusting to class/objects, parts taken from sass.py
#

import os, time, subprocess, uuid
from netCDF4 import Dataset
from abc import ABCMeta, abstractmethod
import numpy as np

class NC(object):
    """
    Class documentation: This root 'nc' class is an abstract class.
    It will be the base to make a netcdf file.
    Its children are 'cdip' and 'sccoos' (grandchildren 'sass' & 'caf')

    .. note::
        | Assume: nc files end in YYYY.nc
        | 'time' variable in data/ncfile
    """
    __metaclass__ = ABCMeta

    #set some initial metadata
    @abstractmethod
    def __init__(self):
        ''' .. note: default metadata values CAN be overwritten in inherited children!'''
        #super(NC, self).__init__()
        #print "init nc"
        self.dateformat = "%Y-%m-%dT%H:%M:%SZ"
        self.metaDict = {
            ##base metadata, can be overwritten
            ##Meta
            'ncei_template_version':"NCEI_NetCDF_TimeSeries_Orthogonal_Template_v2.0",
            'featureType':"timeSeries",
            'Metadata_Conventions':'Unidata Dataset Discovery v1.0',
            'Conventions':'CF-1.6, ACDD-1.3',
            'keywords':'EARTH SCIENCE, OCEANS',
            'keywords_vocabulary':'Global Change Master Directory (GCMD) Earth Science Keywords',
            'standard_name_vocabulary':'CF Standard Name Table (v28, 07 January 2015)',
            'institution':'Scripps Institution of Oceanography, University of California San Diego',
            'license':'Data is preliminary and should not be used by anyone.',
            'geospatial_lon_units':'degrees_east',
            'geospatial_lat_units':'degrees_north',
            'time_coverage_units':'seconds since 1970-01-01 00:00:00 UTC',
            'time_coverage_resolution': 'P1S' #prev '1'
            }
        self.meta_lat = {
        # lat = ncfile.createVariable('lat', 'f4')
            'standard_name':'latitude',
            'long_name':'latitude',
            'units':'degrees_north',
            'axis':'Y',
            'comment':'latitude of sensor'
        }

        self.meta_lon = {
        # lon = ncfile.createVariable('lon', 'f4')
            'standard_name':'longitude',
            'long_name':'longitude',
            'units':'degrees_east',
            'axis':'X',
            'comment':'longitude of sensor'
        }
        self.meta_dep = {
        # dep = ncfile.createVariable('depth', 'f4')
            'standard_name':'depth',
            'long_name':'depth',
            'units':'m',
            'axis':'Z',
            'positive':'down',
            'comment':'depth of sensor'
        }

    @abstractmethod
    def createNCshell(self, ncfile):
        """Create a shell of netCDF file (variables, attributes), without data

        :param str ncfile: file name of netCDF to be made, sans-path (uses **ncpath**)
        """
        pass

    @abstractmethod
    def text2nc(self, filename):
        """read texts in specific format and put in panda's dataframe, to be put in nc files

        :param str filename: path+filename of text file to be read (already joined with **logsdir**)

        .. warning::
            When reading file, before adding to NC. Data prior to :func:`nc.NC.getLastDateNC` is
            truncated so previously added data is not duplicated... Should new data contain older
            data (i.e. filling a gap), this will be truncated as well.
        """
        pass

    @abstractmethod
    def text2nc_all(self):
        """Loop through ALL log/text files in **logsdir**'s subdirectories and put in NC files"""
        pass

    @abstractmethod
    def text2nc_append(self):
        """Append only the latest data to NC files.
        This looks at the lastest datetime recorded in a netcdf,
        then appends any recent data to netcdfs."""
        pass

#     def addNCshell_NC(self, ncfile):
#         """When creating new nc file, at some standard metadata
#
#         .. note: Use at the **end** of ``createNCshell``, at least after createVariable of ``time``
#         :param str ncfile: file name of netCDF to be made, sans-path (uses **ncpath**)
#         """
#         lat = ncfile.createVariable('lat', 'f4')
#         lat.standard_name = 'latitude'
#         lat.long_name = 'latitude'
#         lat.units = 'degrees_north'
#         lat.axis = 'Y'
#         lat.comment = 'latitude of sensor'
# #        ncfile.variables['lat'][0] = ips[ip]['lat']
#         lon = ncfile.createVariable('lon', 'f4')
#         lon.standard_name = 'longitude'
#         lon.long_name = 'longitude'
#         lon.units = 'degrees_east'
#         lon.axis = 'X'
#         lon.comment = 'longitude of sensor'
# #        ncfile.variables['lon'][0] = ips[ip]['lon']
#         dep = ncfile.createVariable('depth', 'f4')
#         dep.standard_name = 'depth'
#         dep.long_name = 'depth'
#         dep.units = 'm'
#         dep.axis = 'Z'
#         dep.positive = 'down' #??
#         dep.comment = 'depth of sensor'
# #        ncfile.variables['depth'][0] = ips[ip]['depth']
#
#         return ncfile

    def updateNCattrs_single(self, ncName):
        """on a single file: run when ONLY nc METADATA needs updating, NOT any data

        :param str ncName: file name of netCDF to be made, with path

        .. note::
            Function uses metaDict variables set in various levels of __init__.

        .. todo::
            - Shouldn't delete global attributes set in ``NCtimeMeta`` :
            time_coverage_duration, date_issued, date_modified, time_coverage_start, time_coverage_end
            - Except SASS object now sets ``metaDict`` in ``createNCshell``. Therefore,
            these global attributes won't work with this function.
            These include: title, date_created, history, geospatial_lat/lon/vertical_min/max,
            institution, comment.
        """
        print ncName
        ncfile = Dataset(ncName, 'a', format='NETCDF4')
        #print ncfile.variables.keys()
        #print ncfile.ncattrs()
        print ncfile.__dict__
        ncfile.setncatts(self.metaDict)
        print "EDITED"
        #print ncfile.__dict__.keys()
        #take out attributes that are no longer in the meta dictionary
        for k in ncfile.__dict__.keys():
            if k not in self.metaDict:
                print 'DELETED', k
                ncfile.delncattr(k)
        self.NCtimeMeta(ncfile)
        print "DONE"
        print ncfile.__dict__#.keys()
        ncfile.close()

    def updateNCattrs_all(self):
        """loop through all nc files and apply updates to metadata"""
        filesArr = os.listdir(self.ncpath)
        filesArr.sort()
        ##print "\n" + time.strftime("%c")
        for fn in filesArr:
            filename = os.path.join(self.ncpath, fn)
            ##print "\n" + fn,
            self.updateNCattrs_single(filename)

    def tupToISO(self, timeTup):
        """Only return Day, Hour, Min, Sec in ISO 8601 duration format"""
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', timeTup)
    # Designed, testing NSDate int, may work with epoch (subsec???)

    def ISOduration(self, minTimeS, maxTimeS):
        """returns ISO duration (days, hrs, mins, secs)"""
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
        """Update time metadata values: Calculate, SPECIFIC to file.
        ISO 8601 Time duration"""
        times = ncfile.variables['time'][:]
        minTimeS = min(times)
        maxTimeS = max(times)
        minTimeT = time.gmtime(minTimeS)
        maxTimeT = time.gmtime(maxTimeS)
        # ncfile.time_coverage_start = tupToISO(minTimeT)
        # ncfile.time_coverage_end = tupToISO(maxTimeT)
        # ncfile.time_coverage_duration = ISOduration(minTimeS, maxTimeS)
        # ncfile.date_modified = time.ctime(time.time())
        ncfile.setncatts({
        "time_coverage_start": self.tupToISO(minTimeT),
        "time_coverage_end": self.tupToISO(maxTimeT),
        "time_coverage_duration": self.ISOduration(minTimeS, maxTimeS),
        "date_modified": self.tupToISO(time.gmtime()), #time.ctime(time.time()),
        "date_metadata_modified": self.tupToISO(time.gmtime()), #time.ctime(time.time()),
        "date_issued": self.tupToISO(time.gmtime()), #time.ctime(time.time()),
        "uuid": str(uuid.uuid4())
        })

    def fileSizeChecker(self, ncfilepath):
        """filesize checker/resizer as a NC method.
        Set as 1e6, could be make default and pass as arg"""
        nameOnly = ncfilepath.split('/')[-1]
        if os.path.isfile(ncfilepath):
            fileMb = int(os.path.getsize(ncfilepath) / 1000000)
            # print "Size: Mb", fileMb, ncfilepath
            if fileMb > 10:
                print "file is getting large, resize"
#                tmpfilepath = '/tmp/' + ncfilename
                # temp = '/usr/local/bin/nccopy'
                # temp = '/home/scheim/NCobj/nccopy'
                temp = os.path.join(self.ncpath,'../tmp_nc')
                envPath = r'/home/uproc/anaconda/envs/log2ncEnv/bin/'
                tmpfilepath = os.path.join(temp, nameOnly)
                origSz = os.path.getsize(ncfilepath)
                # print "tmpfilepath", os.path.isdir(temp), tmpfilepath
                # print "ncfilepath", os.path.isfile(ncfilepath), ncfilepath
                # print "envPath", os.path.isdir(envPath), envPath
                if self.crontab == True:
                    subprocess.call(['nccopy', ncfilepath, tmpfilepath], #subprocess.Popen
                    env={"PATH":envPath}
                    )
                else:
                    subprocess.call(['nccopy', ncfilepath, tmpfilepath])
                subprocess.call(['mv', tmpfilepath, ncfilepath])
                print 'RESIZED FILE: prev:', origSz, os.path.getsize(ncfilepath)

    def attrMinMax(self, rt, attr):
        """get variables' min and max and put values into the metadata"""
        if 'flag' not in attr:
            dMin = rt.variables[attr][:].min()
            dMax = rt.variables[attr][:].max()
            # print 'dataToNC attr min/max:',attr, dMin, dMax
            rt.variables[attr].setncatts({'data_min':dMin, 'data_max': dMax})

    def dataToNC(self, ncName, subset, lookup):
        """Take dataframe and put in netCDF (new file or append).
        Assumes there's a 'time' variable in data/ncfile"""
        if not os.path.isfile(ncName):
            ncfile = self.createNCshell(ncName, lookup)
        ncfile = Dataset(ncName, 'a', format='NETCDF4')
        timeLen = len(ncfile.variables['time'][:])


        ## Add the following: remove any entries from the subset that already exist!!!!!!!
        # exist = subset.epoch.isin(ncDep.variables['time'][:]) #
        epochs = subset.index.values.astype('int64') // 10**9
        exist  = subset.index.isin(epochs)
        appDF = subset[-exist]

        # length should be the same for time & all attributes
        ncfile.variables['time'][timeLen:] = epochs
        # ncfile.variables['time'][timeLen:] = subset.index.values.astype(np.int64) // 10**9
        for attr in self.attrArr:
            #atLen = len(ncfile.variables[attr][:])
            ncfile.variables[attr][timeLen:] = subset[attr].values
            self.attrMinMax(ncfile, attr)

        self.NCtimeMeta(ncfile)
        ncfile.close()

#class CDIP(NC):
#    __metaclass__ = ABCMeta
#    @abstractmethod
#    def __init__(self):
#        super(CDIP, self).__init__()
#        #print "init cdip"
#
#    def createNCshell(self, ncfile, sta):
#        ncfile.naming_authority = 'CDIP'

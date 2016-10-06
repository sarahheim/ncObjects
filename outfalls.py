#
# Author Sarah Heim
# Date create: 2016
# Description: adjusting to class/objects, inheriting NC/SASS classes
#   This class is created for Outfall
#

import os, time
import numpy as np
import pandas as pd
# from netCDF4 import Dataset
# from abc import ABCMeta, abstractmethod
import sccoos, qc

class Outfall(sccoos.SCCOOS):
    """Class for SCCOOS's Outfall. Previously CORDC."""
    def __init__(self):
        """Setting up Outfall variables

        .. todo::
        - More meta
        - CF standard names

        .. warning: Just started
        """
        super(Outfall, self).__init__()
        self.logsdir = r'/data/InSitu/OceanOutfalls/Data/SIO03'
        #self.logsdir = r'/mnt/c/Users/sarah/Documents/work/Projects/ASBS/outfalls/Data/SIO03'
        # self.ncpath = r'/data/InSitu/OceanOutfalls/netcdf'
        self.ncpath = r'/mnt/c/Users/sarah/Documents/work/Projects/ASBS/outfalls/netcdf'
        self.ncpath = '/home/scheim/NCobj/outfalls'
        self.txtFnPre = 'station_SIO03-'
        self.txtFnDatePattern = r'%Y%m%d_%H%M'
        self.ncFnPre = 'SIO03_'

        self.attrArr = ['backwash', 'outfall']

        ##Meta
        self.metaDict.update({
            'keywords':'EARTH SCIENCE, OCEANS',##!!!
            'processing_level':'QA/QC has not been performed', ##!!!
            'metadata_link':'www.sccoos.org.progress/data-products/',
            'summary': '''Discharge sources:
Birch Aquarium - indigenous and non-indigenous species discharge, filter backwash seawater
Hubbs Hall - indigenous and non-indigenous species discharge
Electromagnetic Facility (shark tank) - indigenous species discharge
National Marine Fisheries - indigenous species discharge
Seawater Storage Tanks - filtered seawater
Hydraulics Lab - non-species discharge
Scholander Hall - non-species discharge
Keck Center for Ocean Atmosphere Reseach - non-species discharge
Storm water run-off''',
            'project':'Scripps Outfall 3 and Backwash Volumes',
            'processing_level':'QA/QC has not been performed',
            'cdm_data_type':'Station'
#            'geospatial_lat_resolution':'',  # ?
#            'geospatial_lon_resolution':'',  # ?
#            'geospatial_vertical_units':'',  # ???
#            'geospatial_vertical_resolution':'',  # ???
#            'geospatial_vertical_positive':''  # ???
            })

    def createNCshell(self, ncfile, ignore):
        #NOT using: 'pH_aux', 'O2', 'O2sat'
        print "Outfall createNCshell"
        #ncfile.ip = "132.239.92.62"
        self.metaDict.update({"date_created": self.tupToISO(time.gmtime())})
        ncfile.setncatts(self.metaDict)

        # Create Dimensions
        # unlimited axis (can be appended to).
        time_dim = ncfile.createDimension('time', None)
#        name_dim = ncfile.createDimension('name_strlen', size=25)

        #Create Variables
        time_var = ncfile.createVariable(
            'time', np.int32, ('time'), zlib=True)  # int64? Gives error
        # time_var.setncattr({'standard_name':'time', 'long_name': 'time', 'units':'seconds since 1970-01-01 00:00:00 UTC'})
        time_var.standard_name = 'time'
        time_var.units = 'seconds since 1970-01-01 00:00:00 UTC'
        time_var.long_name = 'time'
        time_var.calendar = 'julian'
        time_var.axis = "T"

        temperature = ncfile.createVariable('backwash', 'f4', ('time'), zlib=True)
        temperature.standard_name = '' #?
        temperature.long_name = 'backwash'
        temperature.units = 'gal/min'
        temperature.coordinates = ''
        temperature.instrument = 'instrument1'
        salinity = ncfile.createVariable('outfall', 'f4', ('time'), zlib=True)
        salinity.standard_name = '' #?
        salinity.long_name = 'outfall'
        salinity.units = 'gal/min'
        salinity.coordinates = ''
        salinity.instrument = 'instrument1'

        instrument1 = ncfile.createVariable('instrument1', 'i') #?
        instrument1.make = ""
        instrument1.model = ""
        instrument1.comment = "" #?

        platform1 = ncfile.createVariable('platform1', 'i')
        platform1.long_name = ""
        platform1.ioos_code = "urn:ioos:sensor:sccoos"

        self.addNCshell_SCCOOS(ncfile)
        ncfile.variables['lat'][0] = 32.86616
        ncfile.variables['lon'][0] = -117.2542
        # ncfile.variables['depth'][0] =

        return ncfile

    def text2nc(self, filename):
        #print 'IN text2nc, filename:', filename #for testing!!!

        # Read file into a pnadas dataframe
        col_names = ['date_time', 'station', 'backwash', 'outfall']
        df = pd.read_csv(filename, sep="\t", header=None, error_bad_lines=False, names=col_names,
                             parse_dates=[0], infer_datetime_format=True, index_col=0)

        ## Get the last time stamp recored in this location's NetCDF file.
        lastNC = self.getLastNC(self.ncFnPre)
        # Truncate data to only that which is after last recorded time
        pd_getLastDateNC = pd.to_datetime(self.getLastDateNC(lastNC), unit='s', utc=None)
        df = df[pd.to_datetime(df.index,utc=None) > pd_getLastDateNC ]

        #print df.head()
        #print df.dtypes
        if len(df.index) > 0:
            # Check file size, nccopy to bring size down, replace original file
            ncfilename = self.ncFnPre + str(df.index[0].year) + '.nc'
            filepath = os.path.join(self.ncpath, ncfilename)
            self.dataToNC(filepath, df, '')
            self.fileSizeChecker(filepath)

    def text2nc_all(self):
        mnArr = os.listdir(self.logsdir)
        mnArr.sort()
        for mn in mnArr:
            mnpath = os.path.join(self.logsdir, mn)
            print "\nDir:",mnpath
            ## Ignore 'stat' folder!!!
            if ((mn != 'stats') and os.path.isdir(mnpath)):
                filesArr = os.listdir(mnpath)
                filesArr.sort()
                ##print "\n" + time.strftime("%c")
                for fn in filesArr:
                    startfld = time.time() # time each folder
                    filename = os.path.join(mnpath, fn)
                    #print "\n--" + fn,
                    self.text2nc(filename)

    def text2nc_append(self):
        """Outfall data files are split into date_hour. """
        pass

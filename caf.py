#
# Author Sarah Heim
# Date create: 2016
# Description: adjusting to class/objects, inheriting NC/SASS classes.
#   This class is created for Carlsbad Aquafarm's burkolator dataset
#
import os, time, datetime

import pandas as pd
import numpy as np
# from netCDF4 import Dataset
# from abc import ABCMeta, abstractmethod

import sccoos
import qc

class CAF(sccoos.SCCOOS):
    """Class for SCCOOS's Carlsbad Aquafarm's burkolator. Currently, log files and netCDFs.
    Rename to OA/BURK??"""
    def __init__(self):
        """Setting up CAF variables

        .. todo: add more metadata to metaDict

        .. warning::
            - for text2nc_append: use **CAF_Latest** folder
            - for text2nc_all: use **CAF_sorted**'s folder/subfolders (i.e.2016)
              which may need to be syncing/ files copied from CAF_2016 and CAF_Latest
        """
        super(CAF, self).__init__()
        print "init caf"
        #use this directory for text2nc_append()
        self.logsdir = r'/data/InSitu/Burkolator/data/CarlsbadAquafarm/CAF_Latest/'
        #use this directory for text2nc_all()
#        self.logsdir = r'/data/InSitu/Burkolator/data/CarlsbadAquafarm/CAF_sorted'
        self.ncpath = '/data/InSitu/Burkolator/netcdf'
#        self.ncpath = '/home/scheim/NCobj/CAF'
#        self.fnformat = "CAF_RTproc_%Y%m%d.dat" #!!!
        self.txtFnPre = 'CAF_RTproc_'
        self.crontab = True
        self.txtFnDatePattern = '%Y%m%d%H%M'
        print "self.ncpath", self.ncpath

        self.attrArr = ['temperature', 'temperature_flagPrimary', 'temperature_flagSecondary',
        'salinity', 'salinity_flagPrimary', 'salinity_flagSecondary',
        'pCO2_atm', 'pCO2_atm_flagPrimary', 'pCO2_atm_flagSecondary',
        'TCO2_mol_kg', 'TCO2_mol_kg_flagPrimary', 'TCO2_mol_kg_flagSecondary']
    #     self.attrArr = ['TSG_T', 'TSG_S', 'pCO2_atm', 'TCO2_mol_kg',
    #    'Alk_pTCO2', 'AlkS', 'calcAlk', 'calcTCO2', 'calcpCO2', 'calcCO2aq',
    #    'calcHCO3', 'calcCO3', 'calcOmega', 'calcpH']

        ##Meta
        self.staMeta = {
            'lat': 33.1390,
            'lon': -117.3390
        }

        self.metaDict.update({
            'keywords':'EARTH SCIENCE, OCEANS, SALINITY/DENSITY, SALINITY, OCEAN CHEMISTRY,',##!!!
            'processing_level':'QA/QC has been performed', ##!!!
            'ip':"132.239.92.62",
            'metadata_link':'www.sccoos.org/data/oa/',
            'summary': 'With funding from NOAA and IOOS, and in support of the West Coast' + \
            ' shellfish industry; AOOS, NANOOS, CeNCOOS, and SCCOOS have added Ocean Acidification' + \
            ' monitoring to its ongoing observations of the coastal ocean. This project funds' + \
            ' a CO2 analyzer (Burkolator) that has been developed by scientists at Oregon State' + \
            ' University. The SCCOOS Burkolator is located at the Carlsbad Aquafarm' + \
            ' (carlsbadaquafarm.com) in San Diego and is operated by the Martz Lab at' + \
            ' the Scripps Institution of Oceanography.',
            'project':'Burkolator, Carlsbad Aquafarm',
            'title':'Burkolator: Carlsbad Aquafarm',
            'processing_level':'QA/QC has not been performed',
            'cdm_data_type':'Station',
            'history':'Carlsbad Aquafarm cultivates Mediterranean Blue Mussels,' + \
            ' Pacific Oysters and Ogo. The company has been in operation since 1990 in Carlsbad.',
            'institution': 'Southern California Coastal Ocean Observing System (SCCOOS)' + \
            ' at Scripps Institution of Oceanography (SIO)', #or Carlsbad Aquafarm?
            "geospatial_lat_min": self.staMeta['lat'],
            "geospatial_lat_max": self.staMeta['lat'],
            "geospatial_lon_min": self.staMeta['lon'],
            "geospatial_lon_max": self.staMeta['lon'],
            # 'contributor_role': 'station operation, station funding, data management', #??
            # 'comment':'',
            # "geospatial_vertical_min": self.staMeta['depth'],
            # "geospatial_vertical_max": self.staMeta['depth'],
            # 'contributor_role': 'station operation, station funding, data management',
            # 'geospatial_lat_resolution':'',  # ?
            # 'geospatial_lon_resolution':'',  # ?
            # 'geospatial_vertical_units':'',  # ???
            # 'geospatial_vertical_resolution':'',  # ???
            # 'geospatial_vertical_positive':''  # ???
            })

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
        :param low_reps: for Flat Line check;
        :param high_reps: for Flat Line check; number of repeating to be considered suspect
        :param eps: for Flat Line check; number of repeating to be considered bad
        :param low_thresh: for Spike Test; see qc.spike_check
        :param high_thresh: for Spike Test; see qc.spike_check
        :returns: dataframe with primary and secondary flags added

        Expected kwargs: sensor_span, user_span"""
        data = df[attr].values
        qc2flags = np.zeros_like(data, dtype='uint8')

        # Missing check
        if miss_val is not None:
            qcflagsMiss = qc.check_nulls(data)
            #nothing for secondary flag if missing?

        else:
            qcflagsMiss = np.ones_like(arr, dtype='uint8')

        # Range Check
        # sensor_span = (-5,30)
        # user_span = (8,30)
        if sensor_span is not None:
            qcflagsRange = qc.range_check(data,sensor_span,user_span)
            qc2flags[(qcflagsRange > 2)] = 1 # Range
        else:
            qcflagsRange = np.ones_like(data, dtype='uint8')

        # Flat Line Check
        # low_reps = 2
        # high_reps = 5
        # eps = 0.0001
        if low_reps and high_reps and eps:
            qcflagsFlat = qc.flat_line_check(data,low_reps,high_reps,eps)
            qc2flags[(qcflagsFlat > 2)] = 2 # Flat line
        else:
            qcflagsFlat = np.ones_like(data, dtype='uint8')

        # Spike Test
        # low_thresh = 2
        # high_thresh = 3
        if low_thresh and high_thresh:
            qcflagsSpike = qc.spike_check(data,low_thresh,high_thresh)
            qc2flags[(qcflagsSpike > 2)] = 3 # Spike
        else:
            qcflagsSpike = np.ones_like(data, dtype='uint8')

        # print 'all pre flags:', attr, data[0], type(data[0]), np.isnan(data[0]), qcflagsMiss[0], qcflagsRange[0], qcflagsFlat[0], qcflagsSpike[0]
        # Find maximum qc flag
        qcflags = np.maximum.reduce([qcflagsMiss, qcflagsRange, qcflagsFlat, qcflagsSpike])
        # print 'final primary flags:', attr,   qcflags[0:10]
        # print 'final secondary flags:',attr, qc2flags[0:10]

        # Output flags
        df[attr+'_flagPrimary'] = qcflags
        df[attr+'_flagSecondary'] = qc2flags

        return df

    def createNCshell(self, ncfile, ignore):
        #NOT using: 'pH_aux', 'O2', 'O2sat'
        print "CAF createNCshell"
        #ncfile.ip = "132.239.92.62"
        self.metaDict.update({"date_created": self.tupToISO(time.gmtime())})
        ncfile.setncatts(self.metaDict)
        #Move to NC/SCCOOS class???
        flagPrim_flag_values = bytearray([1, 2, 3, 4, 9]) # 1UB, 2UB, 3UB, 4UB, 9UB ;
        flagPrim_flag_meanings = 'GOOD_DATA UNKNOWN SUSPECT BAD_DATA MISSING'
        flagSec_flag_values = bytearray([0, 1, 2, 3]) # 1UB, 2UB, 3UB, 4UB, 9UB ;
        flagSec_flag_meanings = 'UNSPECIFIED RANGE FLAT_LINE SPIKE'

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
        time_var.calendar = 'julian' #use??
        time_var.axis = "T"

        temperature = ncfile.createVariable('temperature', 'f4', ('time'), zlib=True)
        temperature.standard_name = 'sea_water_temperature'
        temperature.long_name = 'sea water temperature'
        temperature.units = 'celsius'
        temperature.coordinates = ''
        temperature.instrument = 'instrument1'
        temperature_flagPrim = ncfile.createVariable(
            'temperature_flagPrimary', 'B', ('time'), zlib=True)
        temperature_flagPrim.long_name = 'sea water temperature, qc primary flag'
        temperature_flagPrim.standard_name = "sea_water_temperature status_flag"
        temperature_flagPrim.flag_values = flagPrim_flag_values
        temperature_flagPrim.flag_meanings = flagPrim_flag_meanings
        temperature_flagSec = ncfile.createVariable(
            'temperature_flagSecondary', 'B', ('time'), zlib=True)
        temperature_flagSec.long_name = 'sea water temperature, qc secondary flag'
        temperature_flagSec.flag_values = flagSec_flag_values
        temperature_flagSec.flag_meanings = flagSec_flag_meanings

        salinity = ncfile.createVariable('salinity', 'f4', ('time'), zlib=True)
        salinity.standard_name = 'sea_water_salinity'
        salinity.long_name = 'sea water salinity'
        salinity.units = 'psu' #?
        salinity.coordinates = ''
        salinity.instrument = 'instrument1'
        salinity_flagPrim = ncfile.createVariable(
            'salinity_flagPrimary', 'B', ('time'), zlib=True)
        salinity_flagPrim.long_name = 'sea water salinity, qc primary flag'
        salinity_flagPrim.standard_name = "sea_water_practical_salinity status_flag"
        salinity_flagPrim.flag_values = flagPrim_flag_values
        salinity_flagPrim.flag_meanings = flagPrim_flag_meanings
        salinity_flagSec = ncfile.createVariable(
            'salinity_flagSecondary', 'B', ('time'), zlib=True)
        salinity_flagSec.long_name = 'sea water salinity, qc secondary flag'
        salinity_flagSec.flag_values = flagSec_flag_values
        salinity_flagSec.flag_meanings = flagSec_flag_meanings

        pCO2_atm = ncfile.createVariable('pCO2_atm', 'f4', ('time'), zlib=True)
        pCO2_atm.standard_name = 'subsurface_partial_pressure_of_carbon_dioxide_in_sea_water' #SUBsurface?
        pCO2_atm.long_name = 'partial pressure of carbon dioxide'
        pCO2_atm.units = 'uatm'
        pCO2_atm.coordinates = ''
        pCO2_atm.instrument = 'instrument1'
        pCO2_atm_flagPrim = ncfile.createVariable(
            'pCO2_atm_flagPrimary', 'B', ('time'), zlib=True)
        pCO2_atm_flagPrim.long_name = 'partial pressure of carbon dioxide, qc primary flag'
        pCO2_atm_flagPrim.standard_name = "subsurface_partial_pressure_of_carbon_dioxide_in_sea_water status_flag"
        pCO2_atm_flagPrim.flag_values = flagPrim_flag_values
        pCO2_atm_flagPrim.flag_meanings = flagPrim_flag_meanings
        pCO2_atm_flagSec = ncfile.createVariable(
            'pCO2_atm_flagSecondary', 'B', ('time'), zlib=True)
        pCO2_atm_flagSec.long_name = 'partial pressure of carbon dioxide, qc secondary flag'
        pCO2_atm_flagSec.flag_values = flagSec_flag_values
        pCO2_atm_flagSec.flag_meanings = flagSec_flag_meanings

        TCO2m = ncfile.createVariable('TCO2_mol_kg', 'f4', ('time'), zlib=True)
        TCO2m.standard_name = 'mole_concentration_of_dissolved_inorganic_carbon_in_sea_water'
        TCO2m.long_name = 'seawater total dissolved inorganic carbon concentration'
        TCO2m.units = 'umol/kg'
        TCO2m.coordinates = ''
        TCO2m.instrument = 'instrument1'
        TCO2m_flagPrim = ncfile.createVariable(
            'TCO2_mol_kg_flagPrimary', 'B', ('time'), zlib=True)
        TCO2m_flagPrim.long_name = 'seawater total dissolved inorganic carbon concentration, qc primary flag'
        TCO2m_flagPrim.standard_name = "mole_concentration_of_dissolved_inorganic_carbon_in_sea_water status_flag"
        TCO2m_flagPrim.flag_values = flagPrim_flag_values
        TCO2m_flagPrim.flag_meanings = flagPrim_flag_meanings
        TCO2m_flagSec = ncfile.createVariable(
            'TCO2_mol_kg_flagSecondary', 'B', ('time'), zlib=True)
        TCO2m_flagSec.long_name = 'seawater total dissolved inorganic carbon concentration, qc secondary flag'
        TCO2m_flagSec.flag_values = flagSec_flag_values
        TCO2m_flagSec.flag_meanings = flagSec_flag_meanings

        # = ncfile.createVariable('', 'f4', ('time'), zlib=True)
        #.standard_name = ''
        #.long_name = ''
        #.units = ''
        #.coordinates = ''
        #.instrument = 'instrument1'

        #for c in cols:
        #    cVar = ncfile.createVariable(c, 'f4', ('time'), zlib=True)
        #    cVar.long_name = c

        instrument1 = ncfile.createVariable('instrument1', 'i') #Licor??
        instrument1.make = ""
        instrument1.model = ""
        instrument1.comment = "beta Burkelator" #?

        platform1 = ncfile.createVariable('platform1', 'i')
        platform1.long_name = self.metaDict['project']
        platform1.ioos_code = "urn:ioos:sensor:sccoos:carlsbad"

        self.addNCshell_SCCOOS(ncfile)
        ncfile.variables['lat'][0] = self.staMeta['lat']
        ncfile.variables['lon'][0] = self.staMeta['lon']

        return ncfile

    def text2nc(self, filename):
        #print 'IN text2nc, filename:', filename #for testing!!!

        # Read file line by line into a pnadas dataframe
        df = pd.read_csv(filename, sep="\s+", header=2, dtype={'Date':object, 'Time':object})

        # Set date_time to pandas datetime format
        dateformat = "%Y%m%d %H%M%S"
        df['date_time'] = pd.to_datetime(df['Date']+' '+df['Time'], format=dateformat, utc=None)
        # Make date_time an index
        df.set_index('date_time', inplace=True)
        # Drop columns that were merged
        df.drop('Date', axis=1, inplace=True)
        df.drop('Time', axis=1, inplace=True)
        df.columns = map(lambda x: x.replace('\xb5', ''), df.columns)
        df.rename(columns={'TSG_T':'temperature', 'TSG_S':'salinity'}, inplace=True)
        #self.attrArr = df.columns

        df = self.qc_tests(df, 'temperature', miss_val='Nan', sensor_span=(0,120), user_span=(0,30),
        low_reps=60, high_reps=1800, eps=0.0001, low_thresh=0.5, high_thresh=1)
        df = self.qc_tests(df, 'salinity', miss_val='Nan', sensor_span=(0,1000), user_span=(10,35),
        low_reps=60, high_reps=1800, eps=0.0001, low_thresh=0.5, high_thresh=1)
        df = self.qc_tests(df, 'pCO2_atm', miss_val='Nan', sensor_span=(0, 20000), user_span=(0,1300),
        low_reps=20, high_reps=120, eps=0.01, low_thresh=25, high_thresh=50)
        df = self.qc_tests(df, 'TCO2_mol_kg', miss_val='Nan', sensor_span=(0,2500), user_span=(0,2500),
        low_reps=2, high_reps=3, eps=0.01, low_thresh=None, high_thresh=None)

        ## Get the last time stamp recored in this location's NetCDF file.
        lastNC = self.getLastNC("CAF-")
        # Truncate data to only that which is after last recorded time
        pd_getLastDateNC = pd.to_datetime(self.getLastDateNC(lastNC), unit='s', utc=None)
        df = df[pd.to_datetime(df.index,utc=None) > pd_getLastDateNC ]

        #print df.head()
        #print df.dtypes
        if len(df.index) > 0:
            # Group by Year and iterate making/appending to NetCDF files
            # Do this IF its possible there could be previous year in the file
            groupedYr = df.groupby(df.index.year) # is this necessary or can we just grab the year?
            for grpYr in groupedYr.indices:
                # Check file size, nccopy to bring size down, replace original file
                ncfilename = "CAF-" + str(grpYr) + '.nc'
                filepath = os.path.join(self.ncpath, ncfilename)
                self.dataToNC(filepath, df, '')
                self.fileSizeChecker(filepath)

    def text2nc_all(self):
        yrArr = os.listdir(self.logsdir)
        yrArr.sort()
        for yr in yrArr:
            yrpath = os.path.join(self.logsdir, yr)
            if os.path.isdir(yrpath):
                filesArr = os.listdir(yrpath)
                filesArr.sort()
                for fn in filesArr:
                    # print 'log file:', fn
                    if fn.startswith(self.txtFnPre):
                        filepath = os.path.join(yrpath, fn)
                        print 'use log file:', filepath
                        self.text2nc(filepath)
                    else:
                        print 'not using: ', fn

    def text2nc_append(self):
        """CAF data files are set by size. """
        allFilesArr = os.listdir(self.logsdir) #use Latest!!!
        preFilesArr = []
        postFilesArr = []
        lastNC = self.getLastNC('CAF-')
        LRnc = self.getLastDateNC(lastNC)
        print pd.to_datetime(LRnc, unit='s', utc=None).isoformat()
        print "LRnc:", LRnc
        for fn in allFilesArr:
            #print fn
            # directory contains some other files to ignore
            if '.' not in fn and self.txtFnPre in fn:
                dtStr = fn.split('_')[-1]
                #dtEp = time.mktime(time.strptime(dtStr, self.txtFnDatePattern)) #WRONG, tz
                dtEp = pd.to_datetime(dtStr, format=self.txtFnDatePattern, utc=None).value/1e9
                #print fn, dtStr, dtEp, dtEp > LRnc
                if dtEp > LRnc:
                    postFilesArr.append(dtStr)
                    #print fn, dtStr, dtEp
                else: preFilesArr.append(dtStr)
        preFilesArr.sort()
        postFilesArr.sort()
        print "USE files:"
        if len(preFilesArr) > 0:
            print 'appending from (pre): ', preFilesArr[-1]
            self.text2nc(os.path.join(self.logsdir, self.txtFnPre+preFilesArr[-1]))
        #print postFilesArr
        for p in postFilesArr:
            print 'appending from: (post)', p
            self.text2nc(os.path.join(self.logsdir, self.txtFnPre+p))

#c = CAF()
#print c.ncpath
#print c.logsdir
#c.text2nc_all()
#c.text2nc_append()

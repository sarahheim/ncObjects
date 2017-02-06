#
# Author Sarah Heim
# Date create: 2016
# Description: adjusting to class/objects, inheriting NC/SASS classes.
#   This class is created for Carlsbad Aquafarm's burkolator dataset
#
import os, time, datetime

import pandas as pd
import numpy as np
from netCDF4 import Dataset
# from abc import ABCMeta, abstractmethod

import sccoos
# import qc

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
        self.ncFnPre = 'CAF-'
        self.crontab = True
        self.txtFnDatePattern = '%Y%m%d%H%M'
        print "self.ncpath", self.ncpath

        self.attrArr = ['temperature', 'temperature_flagPrimary', 'temperature_flagSecondary',
        'salinity', 'salinity_flagPrimary', 'salinity_flagSecondary',
        'pCO2_atm', 'pCO2_atm_flagPrimary', 'pCO2_atm_flagSecondary',
        'TCO2_mol_kg', 'TCO2_mol_kg_flagPrimary', 'TCO2_mol_kg_flagSecondary']

        ##Meta
        self.staMeta = {
            # 'depth': ,!!!
            'lat': 33.1390,
            'lon': -117.3390
        }

        #match values to text2nc section 
        self.qc_values = { 'temperature': {'miss_val':'Nan', 'sensor_span':(0,120), 'user_span':(10,30),
            'low_reps':4, 'high_reps':120, 'eps':0.0001, 'low_thresh':0.5, 'high_thresh':1 },
            'salinity': {'miss_val':'Nan', 'sensor_span':(20,40), 'user_span':(20,35),
            'low_reps':4, 'high_reps':120, 'eps':0.0001, 'low_thresh':0.5, 'high_thresh':1 },
            'pCO2_atm': {'miss_val':'Nan', 'sensor_span':(200, 1500), 'user_span':(250,800),
            'low_reps':20, 'high_reps':120, 'eps':0.01, 'low_thresh':25, 'high_thresh':50 },
            'TCO2_mol_kg': {'miss_val':'Nan', 'sensor_span':(1900,2300), 'user_span':(1900,2300),
            'low_reps':2, 'high_reps':3, 'eps':0.01, 'low_thresh':None, 'high_thresh':None }
        }

        self.metaDict.update({
            'cdm_data_type':'Station',
            'contributor_name': 'Carlsbad Aquafarm/SCCOOS, SCCOOS/IOOS/NOAA, SCCOOS',
            'contributor_role': 'station operation, station funding, data management', #??
            'creator_email':'info@sccoos.org', #??
            'creator_name':'Scripps Institution of Oceanography (SIO)', # Todd Martz/ Martz Lab?
            'creator_url':'http://sccoos.org', #Martz Lab url?
            "geospatial_lat_min": self.staMeta['lat'],
            "geospatial_lat_max": self.staMeta['lat'],
            "geospatial_lon_min": self.staMeta['lon'],
            "geospatial_lon_max": self.staMeta['lon'],
            'history':'Carlsbad Aquafarm cultivates Mediterranean Blue Mussels,' + \
            ' Pacific Oysters and Ogo. The company has been in operation since 1990 in Carlsbad.',
            'ip':"132.239.92.62",
            'institution': 'Southern California Coastal Ocean Observing System (SCCOOS)' + \
            ' at Scripps Institution of Oceanography (SIO)', #or Carlsbad Aquafarm?
            'keywords':'EARTH SCIENCE, OCEANS, SALINITY/DENSITY, SALINITY, OCEAN CHEMISTRY,',##!!!
            'metadata_link':'http://www.sccoos.org/data/oa/',
            'processing_level':'QA/QC has been performed', ##!!!
            'project':'Burkolator, Carlsbad Aquafarm',
            'references':'http://www.sccoos.org/data/oa/, http://www.carlsbadaquafarm.com/, https://github.com/ioos/qartod',
            'summary': 'With funding from NOAA and IOOS, and in support of the West Coast' + \
            ' shellfish industry; AOOS, NANOOS, CeNCOOS, and SCCOOS have added Ocean Acidification' + \
            ' monitoring to its ongoing observations of the coastal ocean. This project funds' + \
            ' a CO2 analyzer (Burkolator) that has been developed by scientists at Oregon State' + \
            ' University. The SCCOOS Burkolator is located at the Carlsbad Aquafarm' + \
            ' (carlsbadaquafarm.com) in San Diego and is operated by the Martz Lab at' + \
            ' the Scripps Institution of Oceanography.',
            'title':'Burkolator: Carlsbad Aquafarm',
            # 'comment':'', !!!
            # "geospatial_vertical_min": self.staMeta['depth'],
            # "geospatial_vertical_max": self.staMeta['depth'],
            # 'geospatial_lat_resolution':'',  # ?
            # 'geospatial_lon_resolution':'',  # ?
            # 'geospatial_vertical_units':'',  # ???
            # 'geospatial_vertical_resolution':'',  # ???
            # 'geospatial_vertical_positive':''  # ???
            })

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

        # Create Dimensions
        # unlimited axis (can be appended to).
        time_dim = ncfile.createDimension('time', None)
#        name_dim = ncfile.createDimension('name_strlen', size=25)

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

        temperature = ncfile.createVariable('temperature', 'f4', ('time'), zlib=True)
        temperature.setncatts({
            'long_name':'sea water temperature',
            'standard_name':'sea_water_temperature',
            'units':'celsius'})
        temperature.setncatts(self.qc_meta('temperature'))
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
            'units':'psu'}) #?
        salinity.setncatts(self.qc_meta('salinity'))
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

        pCO2_atm = ncfile.createVariable('pCO2_atm', 'f4', ('time'), zlib=True)
        pCO2_atm.setncatts({
            'standard_name':'subsurface_partial_pressure_of_carbon_dioxide_in_sea_water', #SUBsurface?
            'long_name':'partial pressure of carbon dioxide',
            'units':'uatm'})
        pCO2_atm.setncatts(self.qc_meta('pCO2_atm'))
        pCO2_atm.setncatts(dup_varatts)
        pCO2_atm_flagPrim = ncfile.createVariable(
            'pCO2_atm_flagPrimary', 'B', ('time'), zlib=True)
        pCO2_atm_flagPrim.setncatts({
            'long_name':'partial pressure of carbon dioxide, qc primary flag',
            'standard_name':"subsurface_partial_pressure_of_carbon_dioxide_in_sea_water status_flag",
            'flag_values':flagPrim_flag_values,
            'flag_meanings':flagPrim_flag_meanings})
        pCO2_atm_flagPrim.setncatts(dup_flagatts)
        pCO2_atm_flagSec = ncfile.createVariable(
            'pCO2_atm_flagSecondary', 'B', ('time'), zlib=True)
        pCO2_atm_flagSec.setncatts({
            'long_name':'partial pressure of carbon dioxide, qc secondary flag',
            'standard_name':"subsurface_partial_pressure_of_carbon_dioxide_in_sea_water status_flag",
            'flag_values':flagSec_flag_values,
            'flag_meanings':flagSec_flag_meanings})
        pCO2_atm_flagSec.setncatts(dup_flagatts)

        TCO2m = ncfile.createVariable('TCO2_mol_kg', 'f4', ('time'), zlib=True)
        TCO2m.setncatts({
            'standard_name':'mole_concentration_of_dissolved_inorganic_carbon_in_sea_water',
            'long_name':'seawater total dissolved inorganic carbon concentration',
            'units':'umol/kg'})
        TCO2m.setncatts(self.qc_meta('TCO2_mol_kg'))
        TCO2m.setncatts(dup_varatts)
        TCO2m_flagPrim = ncfile.createVariable(
            'TCO2_mol_kg_flagPrimary', 'B', ('time'), zlib=True)
        TCO2m_flagPrim.setncatts({
            'long_name':'seawater total dissolved inorganic carbon concentration, qc primary flag',
            'standard_name':"mole_concentration_of_dissolved_inorganic_carbon_in_sea_water status_flag",
            'flag_values':flagPrim_flag_values,
            'flag_meanings':flagPrim_flag_meanings})
        TCO2m_flagPrim.setncatts(dup_flagatts)
        TCO2m_flagSec = ncfile.createVariable(
            'TCO2_mol_kg_flagSecondary', 'B', ('time'), zlib=True)
        TCO2m_flagSec.setncatts({
            'long_name':'seawater total dissolved inorganic carbon concentration, qc secondary flag',
            'standard_name':"mole_concentration_of_dissolved_inorganic_carbon_in_sea_water status_flag",
            'flag_values':flagSec_flag_values,
            'flag_meanings':flagSec_flag_meanings })
        TCO2m_flagSec.setncatts(dup_flagatts)


        #for c in cols:
        #    cVar = ncfile.createVariable(c, 'f4', ('time'), zlib=True)
        #    cVar.long_name = c

        instrument1 = ncfile.createVariable('instrument1', 'i') #Licor??
        instrument1.setncatts({
            'make':"",
            'model':"",
            'comment':"beta Burkelator" }) #?

        platform1 = ncfile.createVariable('platform1', 'i')
        platform1.setncatts({
        'long_name':self.metaDict['project'],
        'ioos_code':"urn:ioos:sensor:sccoos:carlsbad" })


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

        dep = ncfile.createVariable('depth', 'f4')
        dep.setncatts(self.meta_dep)
        # lat.setncatts({
        #     'valid_min':self.staMeta['depth'],
        #     'valid_max':self.staMeta['depth']
        # })
        # ncfile.variables['depth'][0] = self.staMeta['depth']!!!


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

        #match values to qc_values metadata!!!
        df = self.qc_tests(df, 'temperature', miss_val='Nan', 
        sensor_span=(0,120), user_span=(10,30),
        low_reps=4, high_reps=120, eps=0.0001, low_thresh=0.5, high_thresh=1)
        df = self.qc_tests(df, 'salinity', miss_val='Nan', 
        sensor_span=(20,40), user_span=(20,35),
        low_reps=4, high_reps=120, eps=0.0001, low_thresh=0.5, high_thresh=1)
        df = self.qc_tests(df, 'pCO2_atm', miss_val='Nan', 
        sensor_span=(200, 1500), user_span=(250,800),
        low_reps=20, high_reps=120, eps=0.01, low_thresh=25, high_thresh=50)
        df = self.qc_tests(df, 'TCO2_mol_kg', miss_val='Nan', 
        sensor_span=(1900,2300), user_span=(1900,2300),
        low_reps=2, high_reps=3, eps=0.01, low_thresh=None, high_thresh=None)

        ## Get the last time stamp recored in this location's NetCDF file.
        lastNC = self.getLastNC(self.ncFnPre)
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
                ncfilename = self.ncFnPre + str(grpYr) + '.nc'
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
        lastNC = self.getLastNC(self.ncFnPre)
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

#
# Author Sarah Heim
# Date create: May 2016
# Description: adjusting to class/objects, parts taken from sass.py
#

class root:
    def __init__(self):
        self.dateformat = "%Y-%m-%dT%H:%M:%SZ"

        ##Meta
        self.ncei_template_version = "NCEI_NetCDF_TimeSeries_Orthogonal_Template_v2.0"
        self.featureType = "timeSeries"
        self.Metadata_Conventions = 'Unidata Dataset Discovery v1.0'
        self.Conventions = 'CF-1.6'
        self.keywords = 'EARTH SCIENCE, OCEANS'
        self.keywords_vocabulary = 'Global Change Master Directory (GCMD) Earth Science Keywords'
        self.standard_name_vocabulary = 'CF Standard Name Table (v28, 07 January 2015)'
        self.institution = 'Scripps Institution of Oceanography, University of California San Diego'
        self.license = 'Data is preliminary and should not be used by anyone.'
        self.geospatial_lon_units = 'degrees_east'
        self.geospatial_lat_units = 'degrees_north'
        self.time_coverage_units = 'seconds since 1970-01-01 00:00:00 UTC'

class cdip(root):
    def __init__(self):
        self.naming_authority = 'CDIP'

class sccoos(root):
    def __init__(self):
        ##Meta
        self.naming_authority = 'sccoos.org'
        self.acknowledgment = 'The Southern California Coastal Ocean Observing System (SCCOOS) ' +\
            'is one of eleven regions that contribute to the national U.S. Integrated Ocean Observing System (IOOS).'
        self.publisher_name = 'Southern California Coastal Ocean Observing System'
        self.publisher_url = 'http://sccoos.org'
        self.publisher_email = 'info@sccoos.org'


class sass(sccoos):
    def __init__(self):
        self.logsdir = r'/data/InSitu/SASS/data/'
        self.ncpath = '/data/InSitu/SASS/netcdfs/'
        self.fnformat = "%Y-%m/data-%Y%m%d.dat"

        self.staMeta = {'UCSB': {'loc': 'stearns_wharf',
                    'loc_name': 'Stearns Wharf',
                    'lat': 34.408,
                    'lon': -119.685,
                    'depth': '2',
                    'url': 'http://msi.ucsb.edu/',
                    'inst': 'Marine Science Institute at University of California, Santa Barbara'},
           'UCI': {'loc': 'newport_pier',
                   'loc_name': 'Newport Pier',
                   'lat': 33.6061,
                   'lon': -117.9311,
                   'depth': '2',
                   'url': 'http://uci.edu/',
                   'inst': 'University of California, Irvine'},
           'UCLA': {'loc': 'santa_monica_pier',
                    'loc_name': 'Santa Monica Pier',
                    'lat': 34.008,
                    'lon': -118.499,
                    'depth': '2',
                    'url': 'http://environment.ucla.edu/',
                    'inst': 'Institute of the Environment at the University of California, Los Angeles'},
           'UCSD': {'loc': 'scripps_pier',
                    'loc_name': 'Scripps Pier',
                    'lat': 32.867,
                    'lon': -117.257,
                    'depth': '5',
                    'url': 'https://sccoos.org/',
                    'inst': 'Southern California Coastal Ocean Observing System (SCCOOS) at Scripps Institution of Oceanography (SIO)'}}

        # IP Address of Shorestations
        self.ips = {'166.148.81.45': staMeta['UCSB'],
       '166.241.139.252': staMeta['UCI'],
       '166.241.175.135': staMeta['UCLA'],
       '132.239.117.226': staMeta['UCSD'],
       '172.16.117.233': staMeta['UCSD']}

        # header names to dat log files
        self.columns = ['server_date', 'ip', 'temperature', 'conductivity', 'pressure', 'aux1',
           'aux3', 'chlorophyll', 'aux4', 'salinity', 'dateDay', 'dateMon',
           'dateYr', 'time', 'sigmat', 'diagnosticVoltage', 'currentDraw']

        self.attrArr = ['temperature', 'conductivity', 'pressure', 'aux1', 'aux3', 'chlorophyll',  # NOT INCLUDING 'time'
           'conductivity_flagPrimary', 'conductivity_flagSecondary',
           'pressure_flagPrimary', 'pressure_flagSecondary',
           'salinity_flagPrimary', 'salinity_flagSecondary',
           'chlorophyll_flagPrimary', 'chlorophyll_flagSecondary']


        ##Meta
        self.metadata_link = 'www.sccoos.org.progress/data-products/automateed-shore-stations/'
        self.summary = 'Automated shore station with a suite of sensors that are ' +\
            'attached to piers along the nearshore California coast. ' + \
            'These automated sensors measure temperature, salinity, chlorophyll, turbidity ' + \
            'and water level at frequent intervals in the nearshore coastal ocean.' +\
            'This data can provide local and regional information on mixing and upwelling, ' +\
            'land run-off, and algal blooms.'
        self.keywords = 'EARTH SCIENCE, OCEANS, SALINITY/DENSITY, SALINITY,  OCEAN CHEMISTRY,' +\
            ' CHLOROPHYLL, OCEAN TEMPERATURE, WATER TEMPERATURE, OCEAN PRESSURE, WATER PRESSURE'
        self.project = 'Automated Shore Stations'
        self.processing_level = 'QA/QC have been performed'
        self.cdm_data_type = 'Station'
        self.source = 'insitu observations'

class caf(sccoos):
    def __init__(self):
        self.logsdir = r'/data/InSitu/Burkolator/data/CarlsbadAquafarm/CAF_Latest/'
        self.ncpath = '/data/InSitu/SASS/Burkolator/netcdf'
#        self.fnformat = "CAF_RTproc_%Y%m%d.dat" #!!!

        ##Meta
        self.keywords = 'EARTH SCIENCE, OCEANS, SALINITY/DENSITY, SALINITY,  OCEAN CHEMISTRY,'##!!!
        self.processing_level = 'QA/QC has not been performed' ##!!!



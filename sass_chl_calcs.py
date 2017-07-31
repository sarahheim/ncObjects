import time, os, urllib2, json
# from urllib import quote_plus
import pandas as pd
from StringIO import StringIO

start = time.time()
xlsUrl = r'https://docs.google.com/spreadsheets/d/1099lNMJ3XZQIFv7oSr0Q-5i4fihx7gnvoxMaVhiUhJE/gviz/tq'
mainQryUrl = r'&tq=SELECT+A,H,I+WHERE+A+IS+NOT+NULL+AND+I+IS+NOT+NULL'
columns = ['date', 'offset', 'scale']
jFile = r'sass_calcs.json'
dateformat = "%Y-%m-%dT%H:%M:%SZ"

stations = {
    'scripps_pier': {
        'baseUrl': xlsUrl+'?gid=533828951',
        'qryUrl': r'&tq=SELECT+A,H,I,J+WHERE+A+IS+NOT+NULL+AND+I+IS+NOT+NULL',
        'columns':['date', 'offset', 'scale', 'time']
    },
    'newport_pier': {
        'baseUrl': xlsUrl+'?gid=264494544',
        'qryUrl': mainQryUrl,
        'columns':columns
    },
    'santa_monica_pier': {
        'baseUrl': xlsUrl+'?gid=1947704850',
        'qryUrl': mainQryUrl,
        'columns':columns
    },
    'stearns_wharf': {
        'baseUrl': xlsUrl+'?gid=1712191100',
        'qryUrl': mainQryUrl,
        'columns':columns
    }
}

if os.path.isfile(jFile):
    with open(jFile) as json_file:
        calcs = json.load(json_file)
else:
    calcs = {}

def staXls2json(sta):
    url = (stations[sta]['baseUrl']+r'&tqx=out:csv'+stations[sta]['qryUrl'])
    # print url
    connection = urllib2.urlopen(url)
    urlCode = connection.getcode()
    print sta, 'getcode:', urlCode
    df = None
    if urlCode == 200:
        doc = connection.read()
        # lines = doc.splitlines()
        data = StringIO(doc)
        df = pd.read_csv(data, header=0, infer_datetime_format=True,
            names=stations[sta]['columns']) #index_col=0
        #make sure that data is collected
        print 'DF len', len(df)
        if len(df) > 0:
            if 'time' in df.columns:
                print 'check time values'
                df['time'].fillna('00:00:00', inplace=True)
                df['date_time']= pd.to_datetime(df.date+'T'+df.time,
                    utc=None, infer_datetime_format=True) #format=dateformat, unit='s'
                df.drop('time', axis=1, inplace=True)
            else:
                print 'No time column'
                df['date_time']= pd.to_datetime(df.date+'T00:00:00Z',
                    utc=None, infer_datetime_format=True) #format=dateformat, unit='s'

            df = df.dropna()
            df.drop('date', axis=1, inplace=True)
            #entries are already sorted
            # df.sort_values('date_time', inplace=True) #sorting my flip entries that have the same date_time
            print 'DF len', len(df)
            print df

            # df.drop_duplicates(inplace=True)
            df.drop_duplicates(['offset', 'scale'], keep='first', inplace=True)
            df['date_time'] = df.date_time.dt.strftime(dateformat)
            df.set_index('date_time', inplace=True)

            df['function'] = 'calc_factorOffset1'
            print 'DF len', len(df)
            print df

        else:
            print 'error with reading csv'
    connection.close()
    
    if os.path.isfile(self.extsDictFn):
        if (df is not None) and (len(df)>0):
            jFile = 'sass_'+sta+'_archive-test.json'
            #Read the json first
            with open(jFile) as json_file:
                extDict = json.load(json_file)
            #Keep ALL other part of json, ONLY editing calcs for chlorophyll
            extDict['calcs']['chlorophyll']

            with open(jFile, 'w') as json_file:
                json.dump(extDict, json_file, indent=4) #indent=2, sort_keys=True
        else:
            "Error: empty dataframe"
    else:
        print 'Missing JSON file' #json file should exist with 'cols'
    print 'Done! calcs to json:', jFile

# staXls2json('scripps_pier')
# staXls2json('santa_monica_pier')
# staXls2json('newport_pier')

def allStations():
    for sta in stations:
        # sta = 'scripps_pier'
        print "station", sta
        staXls2json(sta)

allStations()

import time, os, urllib2, json
# from urllib import quote_plus
import pandas as pd
from StringIO import StringIO

start = time.time()
xlsUrl = r'https://docs.google.com/spreadsheets/d/1099lNMJ3XZQIFv7oSr0Q-5i4fihx7gnvoxMaVhiUhJE/gviz/tq'
mainQryUrl = r'&tq=SELECT+A,H,I+WHERE+A+IS+NOT+NULL+AND+I+IS+NOT+NULL'
ThrCols = ['date', 'offset', 'scale']
qryWithTimeUrl = r'&tq=SELECT+A,H,I,J+WHERE+A+IS+NOT+NULL+AND+I+IS+NOT+NULL'
columnsWithTime = ['date', 'offset', 'scale', 'time']
jFile = r'sass_calcs.json'
dateformat = "%Y-%m-%dT%H:%M:%SZ"

class Station(object):
    def __init__(self, name, **kwargs):
        self.name = name
        allowed_keys = set(['baseUrl', 'qryUrl', 'columns'])
        # initialize all allowed keys to false
        self.__dict__.update((key, False) for key in allowed_keys)
        # and update the given keys by their given values
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)

    def __str__(self):
        return "Station:'{}' \n['{}']".format(self.name, self.columns)

ucsb = Station('stearns_wharf',
    baseUrl= xlsUrl+'?gid=1712191100',
    qryUrl= mainQryUrl,
    columns = ThrCols)

uci = Station('newport_pier',
    baseUrl= xlsUrl+'?gid=264494544',
    qryUrl = qryWithTimeUrl,
    columns = columnsWithTime)

ucla = Station('santa_monica_pier',
    baseUrl= xlsUrl+'?gid=1947704850',
    qryUrl= qryWithTimeUrl,
    columns = columnsWithTime)

ucsd = Station('scripps_pier',
    baseUrl= xlsUrl+'?gid=533828951',
    qryUrl= qryWithTimeUrl,
    columns = columnsWithTime)

if os.path.isfile(jFile):
    with open(jFile) as json_file:
        calcs = json.load(json_file)
else:
    calcs = {}

def staXls2json(sta):
    url = (sta.baseUrl+r'&tqx=out:csv'+sta.qryUrl)
    # print url
    connection = urllib2.urlopen(url)
    urlCode = connection.getcode()
    print sta.name, 'getcode:', urlCode
    df = None
    if urlCode == 200:
        doc = connection.read()
        # lines = doc.splitlines()
        data = StringIO(doc)
        df = pd.read_csv(data, header=0, infer_datetime_format=True,
            names=sta.columns) #index_col=0
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
            df['input'] = df[['scale', 'offset']].values.tolist() #[df.scale, df.offset]
            df.drop('scale', axis=1, inplace=True)
            df.drop('offset', axis=1, inplace=True)
            df['date_time'] = df.date_time.dt.strftime(dateformat)
            df.set_index('date_time', inplace=True)

            df['function'] = 'calc_factorOffset1'
            print 'DF len', len(df)
            print df

        else:
            print 'error with reading csv'
    connection.close()

    jFile = 'sass_'+sta.name+'_archive.json'
    if os.path.isfile(jFile):
        if (df is not None) and (len(df)>0):
            #Read the json first
            with open(jFile) as json_file:
                extDict = json.load(json_file)
            #Keep ALL other part of json, ONLY editing calcs for chlorophyll
            extDict['calcs']['chlorophyll'] = json.loads(df.to_json(None, orient="index", date_format='iso', force_ascii=False))

            with open(jFile, 'w') as json_file:
                json.dump(extDict, json_file, indent=2, sort_keys=True) #indent=4,
        else:
            "Error: empty dataframe"
    else:
        print 'Missing JSON file' #json file should exist with 'cols'
    print 'Done! calcs to json:', jFile

staXls2json(ucsd)

def allStations():
    for ss in [ucsb, uci, ucla, ucsd]:
        # sta = 'scripps_pier'
        print ss
        staXls2json(ss)

# allStations()

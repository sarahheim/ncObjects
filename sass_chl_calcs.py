import time, os, urllib2, json
# from urllib import quote_plus
import pandas as pd
from StringIO import StringIO

start = time.time()
xlsUrl = r'https://docs.google.com/spreadsheets/d/1099lNMJ3XZQIFv7oSr0Q-5i4fihx7gnvoxMaVhiUhJE/gviz/tq'
mainQryUrl = r'&tq=SELECT+A,H,I+WHERE+A+IS+NOT+NULL+AND+I+IS+NOT+NULL'
jFile = r'sass_calcs.json'
dateformat = "%Y%m%dT%H:%M:%SZ"

stations = {
    'scripps_pier': {
        'baseUrl': xlsUrl+'?gid=533828951',
        'qryUrl': mainQryUrl
    },
    'newport_pier': {
        'baseUrl': xlsUrl+'?gid=264494544',
        'qryUrl': mainQryUrl
    },
    'santa_monica_pier': {
        'baseUrl': xlsUrl+'?gid=1947704850',
        'qryUrl': mainQryUrl
    },
    'stearns_wharf': {
        'baseUrl': xlsUrl+'?gid=1712191100',
        'qryUrl': mainQryUrl
    }
}

if os.path.isfile(jFile):
    with open(jFile) as json_file:
        calcs = json.load(json_file)
else:
    calcs = {}

for sta in stations:
    # sta = 'scripps_pier'
    url = (stations[sta]['baseUrl']+r'&tqx=out:csv'+stations[sta]['qryUrl'])
    # print url
    connection = urllib2.urlopen(url)
    urlCode = connection.getcode()
    print sta, 'getcode:', urlCode
    if urlCode == 200:
        doc = connection.read()
        # lines = doc.splitlines()
        data = StringIO(doc)
        df = pd.read_csv(data, header=0, infer_datetime_format=True,
            names=['date', 'offset', 'scale']) #index_col=0
        # print df#.head(3)
        #make sure that data is collected
        if len(df) > 0:
            # df['time'] = df.index % 24 #TEMP FAKE TIME!!!!!
            df['time'] = ['0'+str(i%10)+':00:00' for i in df.index]
            # df['time'] = ['01:23:45' if i%2==0  else '21:48:59' for i in df.index]

            df['date_time']= pd.to_datetime(df.date+' '+df.time,
                utc=None, infer_datetime_format=True, format=dateformat) #format=dateformat, unit='s'
            df.set_index('date_time', inplace=True)
            df.drop('date', axis=1, inplace=True)
            df.drop('time', axis=1, inplace=True)
            df['function'] = 'math1'
            # print df

            if sta not in calcs: calcs[sta]= {}
            # calcs[sta]['chl'] = df.to_json(None, orient="index", date_format='iso', force_ascii=False)
            calcs[sta]['chl'] = json.loads(df.to_json(None, orient="index", date_format='iso', force_ascii=False))
            # calcs[sta]['chl'] = df.to_dict(orient="index") # does NOT take: date_format='iso'
            # print calcs

        else:
            print 'error with reading csv'
    connection.close()

with open(jFile, 'w') as json_file:
    json.dump(calcs, json_file, indent=2)
# json.dump(calcs, jFile, indent=4) #indent=4, sort_keys=True
print 'Done! Wrote sass-chl calcs to json:', jFile

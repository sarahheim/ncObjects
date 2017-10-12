import os, time
import pandas as pd

def allStations(stations, postName):
    dict = {}
    for s in stations:
        fname  = s+postName
        dict[s] = pd.read_csv(fname, index_col=0)

    allPn = pd.Panel(dict)
    print allPn.shape
    divs = ''
    jsCharts = ''
    for i, v in enumerate(allPn.major_axis):
        divs += '<div id="container{}" style="height: 200px; min-width: 310px"></div>\n'.format(i)
        print v#, allPn.major_xs(v)
        seriesArr = []
        for s in allPn.major_xs(v):
            seriesArr.append({'name': s, 'data':allPn[s, v, :].fillna('null').tolist()})
        # print allPn.minor_axis[0]
        jsCharts += '''
$('#container{}').highcharts({{
    title : {{ text : "" }},
    subtitle : {{ text : "{}" }},
    yAxis: {{ title: {{ text: "Flags" }} }},
    plotOptions: {{ series: {{ pointStart: {} }} }},
    tooltip: {{ shared: true }},
    series : {}
}}); '''.format(i, v, allPn.minor_axis[0], seriesArr)
    # print allPn[s, v, :].tolist()

    html = open(postName.split('.')[0]+'.html', 'w')
    html.write('''<!DOCTYPE html>
<html>
<head>
<title>Flag Stats</title>
<style>
div {{
border-style: solid none;
border-width: thin;
}}
</style>
<script src="http://code.jquery.com/jquery-1.11.2.min.js"></script>
<script src="http://code.highcharts.com/stock/highstock.js"></script>
<script src="http://code.highcharts.com/stock/modules/exporting.js"></script>

<script>
$(function () {{
{}
}});
</script>
</head>
<body>
<h1>{}<h1>
{}
</body>
</html>'''.format(jsCharts, postName, divs))
    html.close()

# allStations(['ucsb', 'uci', 'ucla', 'ucsd'], '_v1.csv')
allStations(['ucsb', 'uci', 'ucla', 'ucsd'], '_v4.csv')

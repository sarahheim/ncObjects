import time
start = time.time()

# import os

#OLD
# import sass
# s = sass.SASS()
# s.ncpath = '/data/InSitu/SASS/netcdfs_new/'
# print s.ncpath
# #s.text2nc_all()
# s.text2nc_append()

#NEW
import sass_oop
## to edit ncpath without touching code
# testdir = r'/data/Junk/thredds-test/v3'
# ucsb = sass_oop.SASS_Basic(sass_oop.ucsb)
# ucsb.ncpath = testdir
# ucsb.text2nc_append()

# sass_oop.SASS_Basic(sass_oop.ucsb).text2nc_append()
ucsb = sass_oop.SASS_Basic(sass_oop.ucsb)
# Stearns Wharf is now coming in a new port as of 2/26/18
ucsb.logsdir = r'/data/InSitu/SASS/raw_data/stearns_wharf'
ucsb.text2nc_append()

# sass_oop.SASS_Basic(sass_oop.ucla).text2nc_append() #No longer running
sass_oop.SASS_Basic(sass_oop.ucsd).text2nc_append()

# Newport Pier no longer "Basic"
#sass_newport_pier_archive.json: should have cols: 2016-10-11
sass_oop.SASS_NPd2(sass_oop.uci).text2nc_append()

# Newport ph
# sass_oop.SASS_pH(sass_oop.uci2).text2nc_append()

print "Done!", time.asctime(),"Runtime:", time.time()-start

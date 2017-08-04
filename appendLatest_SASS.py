import time
start = time.time()
import sass

# import os

s = sass.SASS()
s.ncpath = '/data/InSitu/SASS/netcdfs_new/'
print s.ncpath
#s.text2nc_all()
s.text2nc_append()

print "Done!", time.asctime(),"Runtime:", time.time()-start

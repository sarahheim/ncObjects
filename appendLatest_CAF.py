import time
start = time.time()
import caf

#import os
c = caf.CAF()
#c.logsdir = r'/data/InSitu/Burkolator/data/CarlsbadAquafarm/CAF_sorted'
#print c.logsdir
#print c.ncpath
#single = os.path.join(c.logsdir, '2015', 'CAF_RTproc_201502140037')
#print "single file:", single
#c.text2nc(single)
#c.text2nc_all()
c.text2nc_append()

print "Done!", time.asctime(),"Runtime:", time.time()-start

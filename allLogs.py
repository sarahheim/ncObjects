import time
start = time.time()

#json? start with blank?
import dm_mooring as dmm
#Run syncFtpLogs separately. Since files may need manual editing
# import dmm_ftp
# dmm_ftp.syncFtpLogs()
d = dmm.Moor()
#d.logsdir = r'/data/InSitu/'#!!!!!Move to here
d.logsdir = r'/home/scheim/NCobj/delmar_moor'
print d.logsdir
d.ncpath = '/home/scheim/NCobj/DM_Moor'
d.crontab = False
print d.ncpath
d.text2nc_all()

#import caf
#c = caf.CAF()
#c.logsdir = r'/data/InSitu/Burkolator/data/CarlsbadAquafarm/CAF_sorted'
#print c.logsdir
#c.ncpath = '/home/scheim/NCobj/CAF' # Not working, do in sccoos.py
#c.crontab = False
#print c.ncpath
#c.text2nc_all()
##c.text2nc_append()

#import sass
#s = sass.SASS()
#s.logsdir = r'/home/scheim/NCobj/tmp_sass_stearn2017'
#s.ncpath = r'/home/scheim/NCobj/SASS'
#print s.ncpath
#s.crontab = False
#s.text2nc_all()
###s.text2nc_append()

#import sass_v2
#s = sass_v2.SASS()
#s.logsdir = r'/data/InSitu/SASS/raw_data/newport_pier'
#s.ncpath = r'/home/scheim/NCobj/SASS_np'
#s.codedir = r'/home/scheim/NCobj/'
#print s.ncpath
#s.crontab = False
#s.text2nc_all()
##s.text2nc_append()

print "Done!", time.asctime(),"Runtime:", time.time()-start

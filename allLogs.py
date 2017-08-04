import time
start = time.time()

#json? start with blank?
#import dm_mooring as dmm
##Run syncFtpLogs separately. Since files may need manual editing
## import dmm_ftp
## dmm_ftp.syncFtpLogs()
#d = dmm.Moor()
#print d.logsdir
#d.crontab = False
#print d.ncpath
##CT1169100u_11691_20160515.002c.sc1 line 31 needs to be removed first!
#d.text2nc_all('11')
#d.text2nc_all('12')

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

#NEW Aug 2017
import sass_oop
#sass_oop.SASS_Basic(sass_oop.ucsb).text2nc_all()
#sass_oop.SASS_Basic(sass_oop.ucla).text2nc_all()
#sass_oop.SASS_Basic(sass_oop.ucsd).text2nc_all()
##edit sass_newport_pier_archive.json: 2016-10-12
#sass_oop.SASS_Basic(sass_oop.uci).text2nc_all() #crashes after 2016-10-11

sass_oop.SASS_NPd2(sass_oop.uci).text2nc_all()

print "Done!", time.asctime(),"Runtime:", time.time()-start

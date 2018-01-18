import time
start = time.time()

# #json? start with blank?
# import dm_mooring as dmm
# import os
# #Run syncFtpLogs separately. Since files may need manual editing
# # import dmm_ftp
# # dmm_ftp.syncFtpLogs()
# # d = dmm.Moor('11')
# d = dmm.Moor('12')
# print 'logsdir:', d.logsdir
# d.crontab = False
# d.ncpath = r'/data/Junk/thredds-test/DMM'
# print 'ncpath:', d.ncpath
# d.codedir = r'/home/scheim/NCobj'
# print 'codedir:', d.codedir
# d.extsDictFn = os.path.join(d.codedir, r'delmar_mooring_extensions.json')
# print "USING JSON", d.extsDictFn
# #CT1169100u_11691_20160515.002c.sc1 line 31 needs to be removed first!
# # d.text2nc_all()
# d.text2nc_append()

# import caf
# c = caf.CAF()
# #make sure CAF_sorted folder is synced
# c.logsdir = r'/data/InSitu/Burkolator/data/CarlsbadAquafarm/CAF_sorted'
# print c.logsdir
# c.ncpath = r'/data/Junk/thredds-test/CAF'
# c.crontab = False
# print c.ncpath
# c.text2nc_all()
# ##c.text2nc_append()

#NEW Aug 2017
import sass_oop
# otherDir = r'/data/Junk/thredds-test/sass_2017_logs'
otherDir = r'/data/Junk/thredds-test/sass_allNew'
codedir = r'/home/scheim/NCobj'
#sass_oop.SASS_Basic(sass_oop.ucsb).text2nc_all()
#sass_oop.SASS_Basic(sass_oop.ucla).text2nc_all()
#sass_oop.SASS_Basic(sass_oop.ucsd).text2nc_all()
# ucla = sass_oop.SASS_Basic(sass_oop.ucsd)
# ucla.ncpath = otherDir
# ucla.text2nc_all('201')

ucsd = sass_oop.SASS_Basic(sass_oop.ucsd)
ucsd.ncpath = otherDir
ucsd.codedir = codedir
# ucsd.text2nc_all('201')
ucsd.text2nc_append()

ucsb = sass_oop.SASS_Basic(sass_oop.ucsb)
ucsb.ncpath = otherDir
ucsb.codedir = codedir
# ucsb.text2nc_all('201')
ucsb.text2nc_append()

uci = sass_oop.SASS_NPd2(sass_oop.uci)
uci.ncpath = otherDir
uci.codedir = codedir
# uci.text2nc_all('201')
uci.text2nc_append()

# uci2 = sass_oop.SASS_pH(sass_oop.uci2)
# uci2.ncpath = otherDir
# uci2.text2nc_all('201')

##edit sass_newport_pier_archive.json: 2016-10-12
#sass_oop.SASS_Basic(sass_oop.uci).text2nc_all() #crashes after 2016-10-11

# sass_oop.SASS_NPd2(sass_oop.uci).text2nc_all()


print "Done!", time.asctime(),"Runtime:", time.time()-start

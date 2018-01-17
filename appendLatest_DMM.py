import time
start = time.time()
import dm_mooring as dmm
import dmm_ftp

deployment = '12'
# deployment = '11'
dmm_ftp.syncFtpLogs(deployment)
d = dmm.Moor(deployment)
d.text2nc_append()

print "Done!", time.asctime(),"Runtime:", time.time()-start

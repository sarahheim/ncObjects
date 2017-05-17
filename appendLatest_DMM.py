import time
start = time.time()
import dm_mooring as dmm
import dmm_ftp

dmm_ftp.syncFtpLogs()
d = dmm.Moor()
d.text2nc_append()

print "Done!", time.asctime(),"Runtime:", time.time()-start


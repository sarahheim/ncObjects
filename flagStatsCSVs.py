
import time
start = time.time()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sass_oop
testdir = r'/data/Junk/thredds-test/sass_newQC'
uci = sass_oop.SASS_Basic(sass_oop.uci)
# uci.ncpath = testdir
uci.flagStats_allYears('/home/scheim/NCobj/uci_20180109.csv')
ucla = sass_oop.SASS_Basic(sass_oop.ucla)
# ucla.ncpath = testdir
ucla.flagStats_allYears('/home/scheim/NCobj/ucla_20180109.csv')
ucsb = sass_oop.SASS_Basic(sass_oop.ucsb)
# ucsb.ncpath = testdir
ucsb.flagStats_allYears('/home/scheim/NCobj/ucsb_20180109.csv')
ucsd = sass_oop.SASS_Basic(sass_oop.ucsd)
# ucsd.ncpath = testdir
ucsd.flagStats_allYears('/home/scheim/NCobj/ucsd_20180109.csv')


print "Done!", time.asctime(),"Runtime:", time.time()-start


import time
start = time.time()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sass_oop
testdir = r'/data/Junk/thredds-test/sass_2017'
# # Making new netcdfs from OLD netcdfs (original base data, new metadata, new flag values)
# # sass_oop.SASS_Basic(sass_oop.uci).editOldNC('/home/scheim/NCobj/SASS_old/newport_pier-2006.nc')
# sass_oop.SASS_Basic(sass_oop.uci).editOldNCs(testdir)
# sass_oop.SASS_Basic(sass_oop.ucla).editOldNCs(testdir)
# sass_oop.SASS_Basic(sass_oop.ucsb).editOldNCs(testdir)
# sass_oop.SASS_Basic(sass_oop.ucsd).editOldNCs(testdir)
# sass_oop.SASS_NPd2(sass_oop.uci).editOldNCs(testdir)
# sass_oop.SASS_pH(sass_oop.uci2).editOldNCs(testdir)

uci = sass_oop.SASS_NPd2(sass_oop.uci)
uci.ncpath = r'/data/Junk/thredds-test/sass_2017_orig'
uci.editOldNCs(testdir)

ucsb = sass_oop.SASS_Basic(sass_oop.ucsb)
ucsb.ncpath = r'/data/Junk/thredds-test/sass_2017_orig'
ucsb.editOldNCs(testdir)

ucsd = sass_oop.SASS_Basic(sass_oop.ucsd)
ucsd.ncpath = r'/data/Junk/thredds-test/sass_2017_orig'
ucsd.editOldNCs(testdir)

uci2 = sass_oop.SASS_pH(sass_oop.uci2)
uci2.ncpath = r'/data/Junk/thredds-test/sass_2017_orig'
uci2.editOldNCs(testdir)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~
## Update metadata only, but from code structure. Different from man_editMata...
## sass_oop.SASS_Basic(sass_oop.ucsd).updateNCmeta('scripps_pier-2016.nc', '/data/Junk/thredds-test/sass_meta', '')
def all_sass(obj, start, stop):
    for yr in range(start, stop):
        obj.updateNCmeta(obj.prefix+str(yr)+'.nc', '/data/Junk/thredds-test/sass_meta', '')

# all_sass(sass_oop.SASS_Basic(sass_oop.ucsb), 2005, 2018)
# all_sass(sass_oop.SASS_Basic(sass_oop.uci), 2005, 2017)
# all_sass(sass_oop.SASS_Basic(sass_oop.ucla), 2005, 2016)
# all_sass(sass_oop.SASS_Basic(sass_oop.ucsd), 2005, 2018)
# all_sass(sass_oop.SASS_NPd2(sass_oop.uci), 2016, 2018)
# all_sass(sass_oop.SASS_pH(sass_oop.uci2), 2017, 2018)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# import caf
# caf.CAF().updateNCmeta('CAF-2016.nc', '/data/Junk/thredds-test/caf_meta')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# import dm_mooring as dmm
# dmm.Moor().updateNCmeta('48m-2017.nc', '/data/Junk/thredds-test/dmm_meta', 12)

print "Done!", time.asctime(),"Runtime:", time.time()-start

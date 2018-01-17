import ftplib
import time, os, calendar

# logsdir = r'/home/scheim/NCobj/delmar_moor'
logsdir = r'/data/InSitu/DelMar/data'
ftp = ftplib.FTP('geo.ucsd.edu', 'anonymous', 'anonymous')
ftp_log = r'ftp_log.txt'

#if a file has a bad line, it may need to be edited WITHOUT being overwritten.
# Once filename is in this array, it won't be re-copied.
ignoreEdited = ['CT1169100u_11691_20170807.002c.sc1', 'CT1169100u_11691_20171116.002c.sc1', 'CT1169100u_11691_20180109.002c.sc1']
# print ftp.retrlines('LIST')

def copyFTPfile(log, ftp, fn, filename, fnModEp):
    try:
        print "copying", filename
        ftp.retrlines("RETR " + fn, lambda s, w = open(filename, 'w').write: w(s + '\n'))
        os.utime(filename, (time.time(), fnModEp))
    # with open(filename, 'w') as file:
    #     ftp.retrlines("RETR " + fn, file.write)
    # fp = open(filename, 'w')
    # ftp.retrlines('RETR ' + filename, lambda s, w = fp.write: w(s + '\n'))
    # fp.close()
    except ftplib.all_errors as e:
        # print "ERROR copying %s %s" % (filename, e)
        print "ERROR copying {} {}".format(fn, e)
        log.write("ERROR copying {}\n\t{}\n".format(fn, e))
        if os.path.isfile(filename):
            os.remove(filename)

def syncFtpLogs(dpmt):
    ftp.cwd('/pub/songnian/delmar/dmar1_'+dpmt+'/002cal')
    filesArr = ftp.nlst()
    filesArr.sort()
    log = open(ftp_log, 'w')
    for fn in filesArr:
        # print fn
        fnMdtm = ftp.sendcmd('MDTM '+fn)
        fnMod = time.strptime(fnMdtm[4:], "%Y%m%d%H%M%S")
        fnModEp = calendar.timegm(fnMod) #epoch of datetime file was modified
        fnSz = ftp.size(fn)
        #local filename
        filename = os.path.join(logsdir, dpmt, fn)
        #see if local file already exists
        if os.path.isfile(filename):
            # print 'HAVE:', fn
            #check if file size is different
            # WHAT IF FILE NEEDS TO BE EDITED !!!!!!!?!?!??!?!???????
            if (fnSz != os.path.getsize(filename)) and (fn not in ignoreEdited):
                # print '\tDIFF SIZE'
                copyFTPfile(log, ftp, fn, filename, fnModEp)
        else:
            copyFTPfile(log, ftp, fn, filename, fnModEp)

    ftp.quit()
    log.close()
    print "Done FTP script"

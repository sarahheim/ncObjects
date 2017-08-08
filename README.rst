Scripts for creating netCDF files from text/log files. Multiple modules for
different projects. Inheriting shared functions.

Documentation can be found at https://sarahheim.github.io/ncObjects/build/html/

Source code can be found at https://github.com/sarahheim/ncObjects

and https://bitbucket.org/sarahheim/ncobjects

Create all new netCDFs: allLogs.py
Append to existing netCDFs: appendLatest_SASS.py

.. image:: http://www.sccoos.org/static/img/SCCOOS-banner100.jpg

USAGE
=====

#NEW SCCOOS SASS (including Newport)
*/4 * * * * /home/uproc/anaconda/envs/log2ncEnv/bin/python /data/InSitu/SASS/code/ncobjects/appendLatest_SASS.py > ~/appendLatest_sass.out

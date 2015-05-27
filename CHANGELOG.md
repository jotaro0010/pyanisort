##pyAniSort 1.0.4 (May 27, 2015)

* Added support for freeBSD and OS X

## pyAniSort 1.0.3 (February 23, 2014)

* Added an option to compare CRC's of files before and after they are sorted to verify integrity of file transfers
* An option that has the program copy files rather than move them. copied files are not reflected in the history file
* Will now detect if the file is an opening or ending song and will rename it accordingly
* Will save a file with traceback if an unexpected error occurs

## pyAniSort 1.0.2 (February 11, 2014)

* Program files are now created and saved to ~/.pyanisort on Linux and %APPDATA%\pyAniSort on windows
* Short pause between downloads of series xml files. this will help prevent temp bans - February 12, 2014
* Fixed bugs with program data creation on Linux - February 12, 2014
	
## pyAniSort 1.0.1 (February 09, 2014)

* Restructured program so that it could be downloaded and installed through the Python Package Index 
* Created setup.py and init.py
* Program now changes working directory to program location to use data files stored there

## pyAniSort 1.0.0 (February 06, 2014)

* Initial upload

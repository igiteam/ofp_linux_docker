@echo off
rem
rem  Batch file to pack OFP Resistance files for Linux dedicated server
rem  By Kegetys <kegetys@raketti.net>
rem
rem 

echo.

echo This will put files needed by the Linux Dedicated
echo server to an archive servfiles.tar(.gz)
echo.
choice Do you want to continue
IF %ERRORLEVEL% == 2 goto end

echo Copying files to servfiles.tar...
tar -c -v --file=servfiles.tar --files-from=filelist.txt
mkdir xxtempxx
mkdir xxtempxx\res
mkdir xxtempxx\res\dta
copy data.pbo.temp xxtempxx\res\dta\data.pbo >nul
cd xxtempxx
..\tar.exe -v -r --file=../servfiles.tar res/dta/data.pbo
cd ..
del xxtempxx\res\dta\data.pbo
rmdir xxtempxx\res\dta
rmdir xxtempxx\res
rmdir xxtempxx
echo Done

echo.
choice Do you want to include the contents of AddOns dir to the archive
IF %ERRORLEVEL% == 2 goto missions

echo Copying Addons to servfiles.tar...
tar.exe -v -r --file=servfiles.tar addons
echo Done

:missions
echo.
choice Do you want to include the contents of MPMissions dir to the archive
IF %ERRORLEVEL% == 2 goto gzip

echo Copying MP Missions to servfiles.tar...
tar.exe -v -r --file=servfiles.tar mpmissions
echo Done

:gzip
echo.
choice Do you want to GZIP (compress) the archive
IF %ERRORLEVEL% == 2 goto delete

echo GZIP'ing servfiles.tar...
gzip servfiles.tar
echo done.

:delete
echo.
choice Do you want to delete files used by this batch file?
IF %ERRORLEVEL% == 2 goto end

del filelist.txt
del data.pbo.temp
del tar.exe
del gzip.exe
del svm_readme.txt
echo All done. (ignore following error)
del mksvfiles.bat

:end

echo done.

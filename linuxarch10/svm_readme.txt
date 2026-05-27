---------------------------------------------------------
     ·: OFPR Linux server file archiver v1.0 :·
---------------------------------------------------------

This batch file will archives files needed by the OFP
Resistance Linux dedicated server from an OFP Resistance
installation to a TAR archive, which can then be extracted
on a linux machine.

To use, extract all files in this ZIP file to the directory
you have Operation Flashpoint Resistance installed at, and
run "mksvfiles.bat". When the batch file is done, a file
named "servfiles.tar" (or "servfiles.tar.gz" if you chose
to GZip it) will be generated. Take this file to a linux 
machine and extract it, then install the Linux dedicated
server to the directory as instucted in its readme.

The batch file can also archive addons and mpmissions from
the OFP installation, GZIP the TAR archive and then delete
the files used by the batch file. These prodecuders will be 
asked by the batch file when its run.

Without addons and mpmissions the archive file will be about
220MB in size, so ensure you have that much free space on
the drive. GZIP'ing the archive will need more space, but
will decrease the final archive size significantly.

REMEMBER that the tar, or gz file will have copyrighted
material in it from Operation Flashpoint so distributing
it for other than your own use is illegal!

---------------------------------------------------------
By Kegetys <kegetys@raketti.net>
http://ofp.kege.cjb.net
---------------------------------------------------------
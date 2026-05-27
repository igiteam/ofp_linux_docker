Operation Flashpoint: Resistance - Linux Standalone Server 1.96
===============================================================

Copyrigt (c) 2002-2003 Bohemia Interactive Studio and Codemasters. All rights reserved.


    Installation instructions:
    ==========================

1. Following programs must have been installed on your Linux-box:
  uudecode, gunzip, gcc. Optional: md5sum (for setup integrity check)

1a. On some newer verions of Linux (this was reported for RedHat 9
  and Gentoo linux 2.4.20) the NSCD deamon must be installed to
  run OFP server successfully. Caching of DNS would be sufficient.

2. Copy the whole "OperationFlashpoint" directory from Windows
  to some Linux-directory (OFP). DON'T DO ANY DATA CONVERSIONS
  (even "dos2unix" translation of text files is not necessary).
  Example: you can use PKZIP (WinZip, PowerArchiver, etc.) on
  Windows and "unzip" on Linux.
     Don't use upper case letters in the OFP directory name
  (/home/bob/ofp will be good, /home/bob/OperationFlashpoint
  may cause some troubles).
     OFP directory should contain subdirectories "Addons", "Bin",
   "Campaigns", etc.

3. Copy the "server-x.xx.shar.gz" (x.xx is version number) file into
  the OFP directory. Unpack and install it with commands:

  ofp$ gunzip server-x.xx.shar.gz
  ofp$ sh server-x.xx.shar

  Watch the messages - they will inform you whether your installation
  is successful.

4. Dedicated server can be started in foreground:

  ofp$ ./server

  Or in background:

  ofp$ nohup ./server > out.txt 2> err.txt &
  [1] <pid>

5. Running server can be stopped by pressing CTRL+C (foreground)
  or by executing:

  $ kill -s SIGINT <pid>

  Where <pid> is process-id of mother server thread (printed out in
  "nohup" command).

6. From 1.92 OFP server has a new feature: command-line parameter
  "-pid=<pid_file>". It causes creation of <pid_file> with
  PID of root OFP process. If IP port specified in "-port=<nn>"
  parameter is busy (in usage), OFP will terminate immediately
  and <pid_file> won't be written..

7. The "ofpserver" script is provided for automatic server
  start/restart/status query/etc. Please be sure to edit
  CONFIGURATION PARAMETERS in lines 14 to 20 !
  After this is done, install (hard-link?) the script into
  "/etc/rc.d/init.d/ofpserver" file. After that it can be managed
  by "chkconfig" (see info/man).

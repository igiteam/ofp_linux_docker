---------------------------------------------------------
             ·: Spectating Script v1.2 :·
---------------------------------------------------------

This package is for multiplayer mission makers, to include
the script into their missions.

The spectating script allows you to spectate other players
after you die instead of flying around as a seagull.
To include it to your mission, put these files from the
zip into your mission directory:

onPlayerRespawnAsSeagull.sqs
nextCam.sqs
description.ext

If you have something in your description.ext file already
(sound definitions, etc.) put them to the end of this new
description.ext

Edit onPlayerRespawnAsSeagull.sqs with notepad or some other
text editor and change "DeathCamArray" to have an array of
all units to be spectateable. Note that you can also put
AI controlled units and objective vehicles/buildings here
if you want.

Also put the sections from "briefing.txt" into your 
briefing.html. It isn't required, but highly recommended
to let people who play the mission know what the script
is and what it does.

To test the script in preview mode, use the following command:
[0,0,"SeaGull" camCreate [getpos player select 0,getpos player select 1,10]] exec "OnPlayerRespawnAsSeagull.sqs"

-----------------
 Version history
-----------------

* 1.2:

 - Added namelist scrollbox for easy browsing 
   of spectateable players/objects
   
 - Added distance slider to view menu to adjust
   camera distance (zoom in cinematic view)
   
 - Seagull is now properly spawned into the air instead
   of ground when esc is pressed

 - Some minor fixes
   
* 1.1:

 - Workaround for ofp bug which caused the camera not to
   work properly if the spectated unit was in a building. If
   the spectated unit is a vehicle, the bug will still happen.
   
 - If the spectating dialog is closed by pressing esc the
   player will get to the regular seagull mode. Flying above
   150 meters will return to spectating.
   
 - Names are now shown properly for vehicle crew

 - Spectating an empty vehicle will no longer display 
   "Error: no unit" as the unit name

* 1.0:

 - First version


If you have any cutscenes playing during the mission which
change the camera view, do the following after the cutscene
has played to return view to the spectating script camera
for player who have died:

DeathCam cameraEffect ["internal","front"]


By Kegetys <kegetys@dnainternet.net>
http://ofp.kege.cjb.net

---------------------------------------------------------

If you want to distribute this script on your site, you can
do so as long as you keep it free and include all the original 
files in the zip archive unmodified. Any modifications etc.
are allowed as long as proper credit for original author is given

---------------------------------------------------------


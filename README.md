# Subnautica-Base-Generator--Blender-Addon-
Blender Addon That Creates A Base From Videogame "Subnautica" From A Skeleton Mesh

REQUIRED PACKAGES:
	EasyBPY ( follow the instructions on https://curtisholt.online/easybpy)

HOW TO USE:

STEP 1:
	Download "Subnautica_Base_Generator.py" and "subnauticabaseparts.blend". If you want an example of how a skeleton should look like, download "blender addon.blend".

STEP 2:
	With blender open, navigate to the "Edit" tab in the top left, then select "Preferences" from the dropdown menu.
	Click on the "Add-ons" tab on the left side of the "Blender Preferences" window.
	Towards the top right corner of the window, select the button labeled "Install...".
	Navigate in the newly opened file browser to where you installed "Subnautica_Base_Generator.py", select the file, and click "Install Add-on".
	Make sure the box next to "Subnautica Base Generator" is ticked.
	Close out of the "Blender Preferences" window.

STEP 3:
	Make a new "Plane" object from the "Add" menu.
	Press the tab key on your keyboard to go into "Edit Mode".
	Select every vertex by pressing "a" on your keyboard.
	Press "m" on your keyboard, then select "Collapse" from the menu.
	Make sure you are in vertex selection mode by pressing "1" on the number row.
	Start extruding the vertex, but remember that the generator will only work if the edges are exactly one meter long and are at 90 degree angles.

STEP 4:
	Go back into "Object Mode" by pressing the tab key again.
	Make sure your mesh is selected.
	In the "Object" menu in the top left, select the option labeled "Generate Base" in the dropdown (It will appear towards the bottom of the dropdown).
	Navigate to where you downloaded "subnauticabaseparts.blend", select it, and click "Generate Base".
	The process will take a couple of seconds to complete, depending on the size of the skeleton.

# Subnautica-Base-Generator--Blender-Addon-
Blender Addon That Creates A Seabase From A Skeleton Mesh (Inspired By Videogame "Subnautica").

## HOW TO USE:

### STEP 1:

	Download the repository. "blender addon.blend" is not required, but can be used as an example.
	
	Remember to extract everything from the .zip file into a new folder.

### STEP 2:

	With blender open, navigate to the "Edit" tab in the top left, then select "Preferences" from the dropdown menu.
	
	Click on the "Add-ons" tab on the left side of the "Blender Preferences" window.
	
	Towards the top right corner of the window, select the button labeled "Install...".
	
	Navigate in the newly opened file browser to where you installed "Subnautica_Base_Generator.py", select the file, and click "Install Add-on".
	
	Make sure the box next to "Subnautica Base Generator" is ticked.
	
	Close out of the "Blender Preferences" window.

### STEP 3:

	Make a new object object from the "Add" menu.
	
	Press "n" on your keyboard to open the n-panel.
	
	Select the tab that says "Base Gen" on the right side of the 3D viewport.

### STEP 4:

	Make sure you have an object selected.
	In the open panel (top right corner of the 3D viewport), click on the button that says "Select Filepath" (The uppermost option in the panel).
	
	In the newly opened file browser, browse to where you extracted the .zip file.
	
	Select "subnauticabaseparts.blend".
	
	Click on the "Get file" button at the bottom of the file browser window.

## IF YOU ALREADY HAVE A SKELETON YOU WOULD LIKE TO USE, GO TO STEP 5. IF NOT, GO TO STEP 6.

### STEP 5:

	In the "Subnautica Base Generator" panel, click on the option labeled "Base Gen" (The second option).
	
	The last option in the panel is a dropdown menu. This is where you select the quality of your base, out of three different options. Low, Medium, and High quality.
	
	Each quality has its own benefits and drawbacks. Low Quality is the fastest to generate, the fastest to work with, but with the least amount of detail.
	
	Medium Quality, the default option, is still pretty fast to generate, fast to work with, and has more detail than Low Quality.
	
	High Quality is the slowest to generate, and also used to most memory. Be carefult with this option as it might crash Blender. This option has the most detail.
	
	If you have a large enough base (atleast size 50 or above), you can chck the "Generate More Rooms (Skel Gen)" option. This option replaces more corners with rooms. Rooms will never be adjacent to eachother.
	
### STEP 6:

	In the "Subnautica Base Generator" panel, there is an option to change the size of the generated skeleton. Presets: 20 = small | 50 = medium | 100 = large | 200 = extra large.
	The last option in the panel is a dropdown menu. This is where you select the quality of your base, out of three different options. Low, Medium, and High quality.
	
	Each quality has its own benefits and drawbacks. Low Quality is the fastest to generate, the fastest to work with, but with the least amount of detail.
	
	Medium Quality, the default option, is still pretty fast to generate, fast to work with, and has more detail than Low Quality.
	
	High Quality is the slowest to generate, and also used to most memory. Be carefult with this option as it might crash Blender. This option has the most detail.
	
	One of the options on the panel is called "Automatically Generate Base". This option presses the "Base Gen" button for you right after the skeleton is generated.
	
	When you are satisfied with your settings, you can click the "Skel Gen" button (the third option in the panel).

#### Example of a good skeleton:
![image](https://user-images.githubusercontent.com/45775235/127783494-8259f98b-e35f-43bb-a223-9170db2ea2d8.png)

#### Example of a bad skeleton:
![image](https://user-images.githubusercontent.com/45775235/127783549-c988fad1-48cd-4c51-a3ad-b6c3f0339a09.png)

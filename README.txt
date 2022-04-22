
______    _____           _______                                      
| ___ \  |_   _|         | | ___ \                                     
| |_/ /   _| | ___   ___ | | |_/ / __ _ _ __                           
|  __/ | | | |/ _ \ / _ \| | ___ \/ _` | '__|                          
| |  | |_| | | (_) | (_) | | |_/ / (_| | |                             
\_|   \__, \_/\___/ \___/|_\____/ \__,_|_|                             
       __/ |                                                           
      |___/                                                            
______                                      _        _   _             
|  _  \                                    | |      | | (_)            
| | | |___   ___ _   _ _ __ ___   ___ _ __ | |_ __ _| |_ _  ___  _ __  
| | | / _ \ / __| | | | '_ ` _ \ / _ \ '_ \| __/ _` | __| |/ _ \| '_ \ 
| |/ / (_) | (__| |_| | | | | | |  __/ | | | || (_| | |_| | (_) | | | |
|___/ \___/ \___|\__,_|_| |_| |_|\___|_| |_|\__\__,_|\__|_|\___/|_| |_|
                                                                       
                                                                       
PyToolBar - Made by Epsylon - Version 0.2
Automation tools made for Autodesk Maya and Renderman render engine


########################################################################################################
INSTALL STEPS:
	YOU HAVE TO INSTALL THE PYTOOLBAR_02 FOLDER INSIDE A MAYA SCRIPT FOLDER, 
	like a maya/maya2022/scripts/pytoolbar_02/programs.py



	==TO INSTALL PYTHON==
	on the desktop use the shortcut Window+R
	enter "cmd.exe"
	enter "python"
	download it


	===TO INSTALL PYMEL=== 
	To use this package you need to install pymel for python:
	press Window + R
	enter "cmd.exe"
	enter python
	(it will launch Window Store with python selected, download it)
	then return in the Cmd and enter "mayapy -m pip install "pymel>=1.2.,<1.3.""

	if nothing happen you have to go inside the bin folder of maya and try
	to launch the CMD in this folder.
	To do so:

	enter cd /d "C:\Users\path_to_bin_folder\bin\" 

	enter sudo ./mayapy -m pip install "pymel>=1.2.,<1.3." (mac OS)
	enter mayapy -m pip install "pymel>=1.2.,<1.3." (windows OS)


	===TO INSTALL NUMPY===
	press Window + R
	enter cmd.exe
	enter cd "C:\maya_math\Maya_YEAR\bin"

	enter mayapy -m pip install --upgrade numpy (windows OS)
	enter sudo ./mayapy -m pip install --upgrade numpy (mac OS)
########################################################################################################	



TOOLS LIST
	/!\ TOOLS WITH "REWORK" or "NOT ENABLED" MESSAGES MEAN THAT THIS TOOL ISN'T ENABLED IN THE PROGRAM OR 
	THAT IT WILL BE MODIFIED SOON 

	- RIG PANEL
		- Rename Tool 
		- Hook Tool (rework)
		- Center Tool
		- Connexion Tool
		
	- RENDER PANEL
		- Shader Creator Tool (not enabled)
		- Random Lambert Tool (rework)
		- Randomize Tool
		- Basic Light Set Tool (not enabled)
		- Referenced Light Tool (rework)

	- PROJECT TOOL
		- Assets Manager

	- ANIM TOOL
		- EaseIn EaseOut Tool (rework)
		- Switch IK FK
IN NEXT VERSIONS:
	- Hook Tool (rework)
	- Controller Tool 
	- Shader Creator Tool
	- Turn Editor
		- Creation of camera
		- Creation of light set (from selection)
		- Modification of settings in light set 
		- Creation of timing, for rotation (set, and lights)
	- Auto Camera Rig
		- travelling mode
		- zoom in / zoom out

	- Frame Range Library
		- saved in the project
		- creation of bookmarks for each ranges
	- Switch IK / FK Key (rework)
		- creation of bookmarks (for each switch)









########################################################################################################
RENAME TOOL
	This script has 3 modes:
		-replace
		-prefix
		-suffix
	If you are in replace mode the script need 3 informations:
		- the outliner selection
		- something to replace in outliner selection name
		- something to put instead
	else the script only need one information, something to put before or after the outliner selection name
	depending if you are in prefix or suffix mode.


HOOK TOOL
	take (u%2 = 0) informations
	there are two differents cases:
		- 2 items:
			- the first item will be the hooked item, and the second one will be the hooker name
		- (U%2=0) items:
			- U0 (hooked) -> U1 (hooker)
			- U2 (hooked) -> U3 (hooker)
			- ...
			- Un (hooked) -> Un+1 (hooker)

		The script will create a group, which will be moved to the same place as the hooked, the hooked
		item and all children of the hooked item will be moved inside this transform.
		Then the Hooker.WorldParentMatrix[0] will be connected to Hooked.OffsetParentMatrix


CENTER TOOL
	This script take the selection in the outliner / viewport
	It allow you to find the center by creating a Locator at the center of the selection
	You can select vertices and meshes / edges and meshes / meshes to find the center


CONNEXION TOOL
	This script need some origins and target
	attr of origins will go in targets
		-> origin items list
			-> origin attributes list
		-> target items list
			-> target attributes list
	you have several ways to process with items and attributes selection
		- 1 origin ; x target
		- x origin ; x target
		- x origin ; 1 target

		(same things with attributes)

	if you want you can define a constant (number), it will create a MultDoubleLinear node between
	the origin and the target with the constant inside

	if you press CREATE CONNEXIONS the script will try to create each connexions, one by one, if one
	connexion tentative fails, the script will send a notification "connexion origin target failed" and 
	try the next connexions anyway
########################################################################################################




########################################################################################################
RANDOM LAMBERT 
	Assign random 
	lambert to mesh selection 


RANDOMIZE TOOL
	To make this script works you need to select 1 or several items in the outliner
	and 1 or several attributes of these items in the channel box

	Define a min, max value.

	Then you have to mode:
		- Seed will create one random position that you can recreate each time you press Seed
		- Animation will create an animation between two frames
			for that you need to define a delta (time separation between 2 frames)
			- absolute delta : if delta = 2, the delta between 2 frames will be 2 each time
			- relative delta : if delta = 10, the delta between 2 frames will be random between 
			  1 and 10


REFERENCED LIGHT TOOL
	This script allow you to change some of renderman light settings in referenced files from the
	main scene. Basically you don't need to go in the second scene, to change the light and then go back
	to the main scene where you imported this light in reference mode.

	You have to select one or several lights, from one or several referenced maya files and put 
	the settings you want in the Interface.

	This script can only change few settings of renderman Lights :
		intensity
		exposure
		light color
		temperature
		intensity near distance
		cone angle
		cone softness

	You have different elements:
	- An attribute list, that you want to change, you can select several attributes
	- A Define Color button if you want to use the LightColor attribute
	- A Float Field that you can use for all the other attributes

	This script only works if you don't have any issues with references
	Make sure that you don't have those kind of issues, In any case the script won't crash scenes.
	I'm currently working on a new version that is more optimised.
	It works but it's an algorythm that do quite a lot of differents things at the same time
	so it take memories (a bit don't worry).

	This script only works with MayaAscii files (.ma)
########################################################################################################




########################################################################################################
EASE IN EASE OUT TOOL
	Take only one curve selected in the graph Editor and one or several keys selected

	If you press "save Keys" the script will save the position of the keys (before you will deform them)
	If you press "Reset Keys" the script will Set each keys to it initial position (only work if you save)

	Then you have to FloatSlider, each of them define one delta that will move the Bezier influence
	If Both Delta are positive you get an Ease In
	If Both Delta are negative you get an Ease Out
	If one Delta is positive and the other one is negative you get an EaseIn EaseOut


SWITCH IK / FK TOOL 
	This program allow you to create a switch between Ik and Fk on a RIG.
	To do so you have to create a preset for each limbs that you want to switch in your animation,
	for instance, you can create a switch only for the right arm.
	To create a switch you have to define several informations:
		- Joints of the limbs from parents to children (from shouldren to wrist for instance)
		- Controllers FK from parents to children
		- Ik Handle of this limb
		- Instanced attribute / controller that contain the "Switch Ik Fk" attributes
			(it can be anything!)
		- A name for this preset
	Since you have defined those informations you can "CREATE A SWITCH PRESET".
	This preset will be saved on your project in the scripts folder.

	If now you want to switch between ik and FK during animation, you have to now that the program
	will detect if you are in ik or FK by checking max and min value of the switch attribute.
	So let's imagine that you are at the frame 5, in FK, if you select the preset for the right arm
	and define a keyframe of 10, and press the "SWITCH IK FK" button, 10 frames after, the rig
	will be in IK, at the same position, of course it works between IK AND FK too.
########################################################################################################





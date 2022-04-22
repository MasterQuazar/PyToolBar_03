#coding: utf-8
import os
import sys
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import pymel.core as pm
import numpy as np
import imp
import maya.mel as mel
import pickle

from random import randrange
from random import uniform
from importlib import reload
from functools import partial
from pymel import core



#PYTOOLBAR FOR MAYA
#Automation program for maya and renderman in maya

#By Epsylon
#With SirHugo for EaseIn / EaseOut TOOL



def onMayaDroppedPythonFile(*args):
	#create the path for all the functions
	path = '/'.join(__file__.replace("", "/").split("/")[:-1])
	sys.path.append(path)
	print("PATH ADDED TO MAYA")



#look for the path of the program in syspath variables
#check if the function module exists!
exist = False
for item in sys.path:
	if os.path.isdir(os.path.join(item, "PyToolBar_02"))==True:
		folder_path = os.path.join(item, "PyToolBar_02")
		exist = True
if exist == False:
	print("Folder doesn't exist!")
	exit()
os.chdir(folder_path)


try:
	from PyToolBar_02.Modules.PyToolBar_02_RigModula import RigApplication
	from PyToolBar_02.Modules.PyToolBar_02_RenderModula import RenderApplication
	from PyToolBar_02.Modules.PyToolBar_02_AnimModula import AnimApplication
	from PyToolBar_02.Modules.PyToolBar_02_ProjectModula import ProjectApplication
	print("Modules loaded")
except:
	mc.error("Module not found or impossible to import!")
	sys.exit()





class GuiApplication(RigApplication, RenderApplication, AnimApplication, ProjectApplication):
	def __init__(self):
		print(os.getcwd())
		print(os.path.isfile('Data/ModuleManagerData.dll'))
		self.interface_function_list = []
		with open("Data/ModuleManagerData.dll", "r") as read_file:
			for line in read_file.readlines():
				self.interface_function_list.append(line.rstrip())



		self.window_width = 310
		self.window_height = 400
		self.window_mode = "RIG"


		#letter verification function variables
		letter = "abcdefghijklmnopqrstuvwxyz"
		figure = "0123456789"

		self.list_letter = list(letter)
		self.list_capital = list(letter.upper())
		self.list_figure = list(figure)


		#switch ik/fk
		self.joints_list = []
		self.controller_list = []
		self.switch_controller = None
		self.ik_controller = None
		self.keyframe_delta = 1

		self.animation_preset = self.load_animation_preset_function()
		self.animation_preset_name_list = []

		for element in self.animation_preset:
			self.animation_preset_name_list.append(element["name"])


		#referenced lights tool
		self.list_referenced_files = []
		self.list_light_attributes = [
			"intensity",
			"exposure",
			"lightColor",
			"temperature",
			"intensityNearDist",
			"coneAngle",
			"coneSoftness"]

		self.list_light_kind = [
			"PxrRectLight",
			"PxrDiskLight",
			"PxrSphereLight",
			"PxrDistantLight",
			"PxrCylinderLight",
			"PxrDomeLight"
			]
		self.selected_color = [0,0,0]


		#connexion editor variables
		self.list_origin_items = []
		self.list_target_items = []
		self.list_origin_attr = []
		self.list_target_attr = []


		#create shader variables
		self.file_type = ["albedo", "roughness", "bump", "mask"]
		self.default_extension = ".tif"


		#basic light set variables
		self.key_exposure = 9
		self.rim_exposure = 7.5


		#ease in ease out tool
		self.ini_x = []
		self.ini_y = []


		#random light set tool
		self.min_color = [0.0, 0.0, 0.0]
		self.max_color = [1.0, 1.0,1.0]
		self.delta_mode = "Relative"



		#curve saver tool variables
		self.name_list = []
		self.curve_list = []
		try:
			with open("Data/CurveManagerData.dll", "rb") as read_file:
				self.curve_list = pickle.load(read_file)

			for element in self.curve_list:
				self.name_list.append(element["short_name"])
		except:
			pass



		#asset folder manager variables
		project = mc.workspace(query=True, rd=True)
		self.active_folder_list = []
		self.data_folder_list = []
		self.item_type_list = [
			".ma",
			".mb",
			".obj",
			".tex",
			".exr",
			".tif",
			".png",
			".vdb"]

		#change the path of the program
		#check if the program is in sys.path
		exist = False

		self.folder_path = os.getcwd()

		#check if the data file exist
		try:
			with open("PyToolBar_02/Data/AssetsManagerData.dll", "r") as load_file:
				for line in load_file:
					self.data_folder_list.append(line.rstrip())
		except:
			self.data_folder_list = self.create_assets_manager_data_file_function()


		#check if the framerange file exist in the folder
		try:
			with open(os.path.join(project, "scripts/AnimRangeData.dll"), "rb") as read_file:
				self.anim_range_list = pickle.load(read_file)
			self.name_list = []
			for element in self.anim_range_list:
				self.name_list.append("%s [%s ; %s]" % (element["name"], element["min"], element["max"]))
		except:
			self.anim_range_list = []
			self.name_list = []


		#define a path for the directory
		for element in self.data_folder_list:
			if os.path.isdir(element)==True:
				self.active_folder_list.append(element)



		self.main_interface()








	#LETTER VERIFICATION FUNCTION
	def letter_verification_function(self, content):
		if content=="":
			return False
		content = list(content)
		i = 0

		while i < len(content):
			if (content[i] in self.list_letter)==True or (content[i] in self.list_capital)==True or (content[i] in self.list_figure)==True:
				return True
			else:
				if i==(len(content) - 1):
					mc.error("TextField Error, you have to enter something!")
					return False
				else:
					i+=1









	#main interface of the program
	#the interface change depending of the mode
	#	-> RIG / RENDER MODE
	#(0.97, 0.205, 0.249)
	def main_interface(self):
		#CREATION OF THE INTERFACE
		self.window = mc.window(menuBar=True, title="PyToolBar - By Epsylon | Version 0.2 [2022]", sizeable=True, width=self.window_width)
		#self.mainCL = mc.columnLayout(adjustableColumn=True)



		self.form = mc.formLayout(parent = self.window, height=500)
		self.tabs = mc.tabLayout(innerMarginWidth=50, innerMarginHeight=0)
		mc.formLayout( self.form, edit=True, attachForm=((self.tabs, 'top', 0), (self.tabs, 'left', 0), (self.tabs, 'bottom', 0), (self.tabs, 'right', 0)))


		for function in self.interface_function_list:
			result = eval("self.build_%s_interface_function"%function + "()")
		#mc.tabLayout(self.tabs, edit=True, tabLabel=((self.child1, "Rig / modeling"), (self.child2, "Render"), (self.child3, "Animation"), (self.child4, "Project")))
		self.new_window = mc.dockControl(label = "PyToolBar - By Epsylon | Version 0.2 [2022]", area="right", content=self.window, allowedArea=["right", "left"])













		mc.showWindow()













GuiApplication()

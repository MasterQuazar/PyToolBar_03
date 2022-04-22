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

#By Quazar
#With SirHugo for EaseIn / EaseOut TOOL



def onMayaDroppedPythonFile(*args):
	#create the path for all the functions
	path = '/'.join(__file__.replace("", "/").split("/")[:-1])
	sys.path.append(path)
	print("PATH ADDED TO MAYA")


__version__ = "03"
__author__ = "Quazar"

exist = False
for item in sys.path:
	if os.path.isdir(os.path.join(item, "PyToolBar_%s"%__version__))==True:
		__folder__ = os.path.join(item, "PyToolBar_%s"%__version__)
		exist = True
if exist != True:
	mc.error("Folder doesn't exist!")
	exit()
os.chdir(__folder__)

try:
	from PyToolBar_03.Modules.RigM import RigApplication
	from PyToolBar_03.Modules.RenderM import RenderApplication
	from PyToolBar_03.Modules.AnimM import AnimApplication
	from PyToolBar_03.Modules.ProjectM import ProjectApplication
	print("Modules loaded")
except:
	mc.error("Module not found or impossible to import!")
	sys.exit()





class GuiApplication(RigApplication, RenderApplication, AnimApplication, ProjectApplication):
	def __init__(self):
		#check if the module list file exist
		self.project = mc.workspace(query=True, rd=True)

		
		with open(os.path.join(__folder__, "Data/ToolData.dll"), "r") as read_data_file:
			self.pack_list = read_data_file.readlines()
		for i in range(0, len(self.pack_list)):
			self.pack_list[i] = self.pack_list[i].rstrip()



		self.window_width = 310

		letter = 'abcdefghijklmnopqrstuvwxyz'
		figure = '0123456789'
		self.folder_path = os.getcwd()



		#check if the data file exist
		self.data_folder_list = []
		try:
			with open("%s/Data/AssetsManagerData.dll"%__folder__, "r") as load_file:
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

		self.item_type_list = [
			".ma",
			".mb",
			".obj",
			".tex",
			".exr",
			".tif",
			".png",
			".vdb"]
		self.active_folder_list = []
		#define a path for the directory
		for element in self.data_folder_list:
			if os.path.isdir(element)==True:
				self.active_folder_list.append(element)






		#FUNCTIONS VAR
		#ease in ease out tool
		self.ini_x = []
		self.ini_y = []


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


			
		#connexion editor variables
		self.list_origin_items = []
		self.list_target_items = []
		self.list_origin_attr = []
		self.list_target_attr = []




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
		self.pack_function_list = {}

		self.main_interface()



	def main_interface(self):
		"""
		creation of the main interface
		made of a main window (and some main layouts)
		load the differents application (tools) into tabs
		tabs are by default invisible

		checkbox allow them to be visible
		"""
		self.main_window = mc.window(sizeable=False, title="PyToolBar [03] By Quazar", width=self.window_width, height=500, menuBar=True)

		#menubar containing checkbox to enable
		self.menubar = mc.menu(label="Tool List")

		#creation of the scrollbar in the main window
		self.scrollbar = mc.scrollLayout(width=self.window_width + 40, parent=self.main_window)
		self.main_column = mc.columnLayout(adjustableColumn=True, parent=self.scrollbar)
		mc.separator(style="singleDash", height=5)


		#searchbar
		"""
		mc.text(label="Search Bar for tools", parent=self.main_column, width=self.window_width)
		self.main_searchbar = mc.textField(changeCommand=self.searchbar_function, width=self.window_width)
		"""


		for function in self.pack_list:
			result = eval("self.build_%s_interface_function"%function + "()")
		
		self.radiomenubar = mc.radioMenuItemCollection(parent=self.menubar)

		for categorie in self.pack_function_list:
			self.menutag = mc.menuItem(subMenu=True, label=categorie, parent=self.menubar)
			for tool in self.pack_function_list[categorie]:
				self.item = mc.menuItem(label=tool, checkBox=False, parent=self.menutag, command=self.change_tool_visibility_function)


		"""
		for tool in self.pack_function_list:
			self.item = mc.menuItem(label=tool, checkBox=False, parent=self.menubar, command=self.change_tool_visibility_function)
		"""
		self.new_window = mc.dockControl(label="PyToolBar - Made by Quazar - Version 03", area="right", content=self.main_window, allowedArea=["right", "left"])
		mc.showWindow()








	def change_tool_visibility_function(self, event):
		#get the list of items inside the menubar
		menucategories = mc.menu(self.menubar, query=True, itemArray=True)
		visibility_list = []
		tool_list = []
		"""
		for i in range(0, len(menuitems)):
			#get the value of items 
			visibility_list.append(mc.menuItem(self.menubar+"|"+menuitems[i], query=True, checkBox=True))
		for i in range(0, len(self.pack_function_list)):
			functionname = self.pack_function_list[i]
			result = eval("mc.frameLayout(self.%s, edit=True, visible=%s)" % (functionname, visibility_list[i]))"""

		for i in range(0, len(menucategories)):
			menutool = mc.menu(menucategories[i], query=True, itemArray=True)
			for i in range(0, len(menutool)):	
				visibility_list.append(mc.menuItem(self.menubar+"|"+menutool[i], query=True, checkBox=True))
		for element in self.pack_function_list:
			for tool in self.pack_function_list[element]:
				tool_list.append(tool)


		for i in range(0, len(tool_list)):
			functioname = tool_list[i]
			print(functioname, visibility_list[i])
			result = eval( "mc.frameLayout(self.%s, edit=True, visible=%s)" % (functioname, visibility_list[i]) )






	def searchbar_function(self, event):
		searchbar_content = mc.textField(self.main_searchbar, query=True, text=True)
		







GuiApplication()
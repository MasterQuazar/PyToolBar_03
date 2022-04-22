#coding: utf-8
import maya.cmds as mc
import sys
import os
import maya.OpenMaya as OpenMaya
import pymel.core as pm 
import imp 
import maya.mel as mel 
import shutil

from functools import partial





"""
program that allow you to create or load an asset folder in general
	create a main folder assets on your computer
	save project assets in this folder
	import assets from this folder in the project
		-> load in the scene?
		-> create a folder in project scenes folder
"""


#FOLDER LIST -> list of assets folder saved with the program (can be on more than 1 computer)
#ACTIVE FOLDER LIST -> list of assets folder that the program has found on the computer 

class ProjectApplication:
	def build_project_interface_function(self):
		print("ProjectInterface built")
		self.pack_function_list["Project"] = ["AssetManagerTool"]
		"""
		-> create the main folder
		-> load the main folder (if the list isn't empty)
		-> load items from main folder
		-> save items in main folder
		-> brute save (in a whole folder)
		"""

		
		self.AssetManagerTool = mc.frameLayout(visible=False, parent=self.main_column, label="Assets Manager", collapsable=True, collapse=False, width=self.window_width+10, backgroundColor=(0.172, 0.322, 0.071))

		mc.button(label="Save a folder as AssetFolder", command=self.create_asset_folder_function, parent=self.AssetManagerTool)
		mc.button(label="Delete a folder in the list", command=self.delete_asset_folder_function, parent=self.AssetManagerTool)
		
		self.asset_folder_scrolllist = mc.textScrollList(allowMultiSelection=False, numberOfRows=8, enable=True, append=self.active_folder_list, parent=self.AssetManagerTool)

		self.assetmanager_rowcol1 = mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, self.window_width/4)], parent=self.AssetManagerTool)
		self.asset_kind_scrolllist = mc.textScrollList(allowMultiSelection = True, numberOfRows=15, enable=True, parent=self.assetmanager_rowcol1, append=self.item_type_list, selectCommand=self.load_items_type_function)
		
		self.assetmanager_col1 = mc.columnLayout(adjustableColumn=True, parent=self.assetmanager_rowcol1)
		mc.text(label="AssetFolder Assets", parent=self.assetmanager_col1)
		self.asset_scrolllist = mc.textScrollList(allowMultiSelection=True, numberOfRows=8, enable=True, parent=self.assetmanager_col1)
		mc.text(label="Project Assets", parent=self.assetmanager_col1)
		self.project_scrolllist = mc.textScrollList(allowMultiSelection=True, numberOfRows=8, enable=True, parent=self.assetmanager_col1)
	
		
		self.checkbox_autosave_incremental = mc.checkBox(label="Add autosave files", parent=self.AssetManagerTool)
		mc.button(label="Import items in project", command=partial(self.moove_items_function, "import"), parent=self.AssetManagerTool)
		mc.button(label="Export items to AssetFolder", command=partial(self.moove_items_function, "export"), parent=self.AssetManagerTool)
		mc.button(label="Save everything", command=self.export_entire_folder_function, parent=self.AssetManagerTool)





	def project_items_function(self, event):
		project_path = mc.workspace(query=True, rd=True)
		checkbox_selection = mc.checkBox(self.checkbox_autosave_incremental, query=True, value=True)
		asset_type_selection = mc.textScrollList(self.asset_kind_scrolllist, query=True, si=True)
		#look for items in project depending of the extension selected
		project_concerned_files = []

		if asset_type_selection == None:
			return
		for subfolder in os.walk(project_path, topdown=True):
			if checkbox_selection == True:
				if (os.path.split(subfolder[0])[1] == "autosave") or (os.path.split(subfolder[0])[1] == "incrementalSave"):
					continue
			#list all the files
			file_list = subfolder[2]
			if len(file_list) != 0:
				for element in file_list:
					for kind in asset_type_selection:
						if os.path.splitext(element)[1] == kind:
							project_concerned_files.append(os.path.join(subfolder[0],element))
		mc.textScrollList(self.project_scrolllist, edit=True, removeAll=True, append=project_concerned_files)






	def create_assets_manager_data_file_function(self):
		self.data_folder_list = []

		#save a file that contain only an empty list
		with open("Data/AssetsManagerData.dll", "w") as save_file:
			pass
		return self.data_folder_list





	def create_asset_folder_function(self, event):
		self.folder_selection = mc.fileDialog2(dialogStyle=2, fileMode=3)

		
		if self.folder_selection != None:
			#CREATE THE FOLDER AND ITS ARCHITECTURE
			os.mkdir(os.path.join(self.folder_selection[0], "ASSETFOLDER"))
			os.mkdir(os.path.join(self.folder_selection[0], "ASSETFOLDER/IMAGES"))
			os.mkdir(os.path.join(self.folder_selection[0], "ASSETFOLDER/SCENES"))
			os.mkdir(os.path.join(self.folder_selection[0], "ASSETFOLDER/SIMULATION"))

			self.active_folder_list.append(os.path.join(self.folder_selection[0], "ASSETFOLDER"))
			self.data_folder_list.append(os.path.join(self.folder_selection[0], "ASSETFOLDER"))


			#save the new file
			with open("Data/AssetsManagerData.dll", "w") as save_file:
				for item in self.data_folder_list:
					save_file.write(item+"\n")
			#add the new list to the UI
			mc.textScrollList(self.asset_folder_scrolllist, edit=True, removeAll=True, append=self.active_folder_list)
			



	def delete_asset_folder_function(self, event):
		folder_selection = mc.textScrollList(self.asset_folder_scrolllist, query=True, si=True)
		for item in folder_selection:
			self.active_folder_list.remove(item)
			self.data_folder_list.remove(item)
		with open("Data/AssetsManagerData.dll", "w") as save_file:
			for line in self.data_folder_list:
				save_file.write(item+"\n")
		mc.textScrollList(self.asset_folder_scrolllist, edit=True, removeAll=True, append=self.active_folder_list)
		mc.textScrollList(self.asset_scrolllist, edit=True, removeAll=True)






	def export_entire_folder_function(self, event):
		"""
		take a folder selection and export all items that we can find in the extension selection list
		copy those items in the asset folder, in the right folder
		"""
		folder_selection = mc.fileDialog2(dialogStyle=2, fileMode=3)
		if folder_selection == None:
			return
		#if the selection in the extension list is empty, copy all elements in the folder concerned by the extension list
		#	--> full extension list
		destination_selection = mc.textScrollList(self.asset_folder_scrolllist, query=True, si=True)
		extension_selection = mc.textScrollList(self.asset_kind_scrolllist, query=True, si=True)
		if extension_selection == None:
			extension_selection = self.item_type_list



		if destination_selection != None:
			for destination in destination_selection:
				#go through all the items in the target folder
				#check the extension of all files inside
				for subfolder in os.walk(folder_selection[0], topdown=True):
					for file in subfolder[2]:
						extension = os.path.splitext(file)[1]

						if (extension in extension_selection)==True:

							if (extension in [".ma", ".mb", ".obj"])==True:
								final_folder_path = destination + "/SCENES"
							if (extension in [".png", ".tex", ".tiff", ".exr"])==True:
								final_folder_path = destination + "/IMAGES"
							if (extension == ".vdb"):
								final_folder_path = destination + "/SIMULATION"

							try:
								shutil.copy(os.path.join(subfolder[0], file), final_folder_path)
								print("[%s -> %s] MOVED" % (file, final_folder_path))
							except:
								mc.warning("[%s -> %s] FAILED" % (file, final_folder_path))
						








	def moove_items_function(self, command, event):
		if command=="import":
			origin_path = mc.textScrollList(self.asset_folder_scrolllist, query=True, si=True)
			origin_items = mc.textScrollList(self.asset_scrolllist, query=True, si=True)
			destination_path = [mc.workspace(query=True, rd=True)]
		if command == "export":
			origin_path = [mc.workspace(query=True, rd=True)]
			origin_items = mc.textScrollList(self.project_scrolllist, query=True, si=True)
			destination_path = mc.textScrollList(self.asset_folder_scrolllist, query=True, si=True)

		if (origin_path != None) and (origin_items != None) and (destination_path != None):
			for origin in origin_items:
				for destination in destination_path:
					#check the extension of the file
					extension = os.path.splitext(origin)[1]
					if (extension in (self.item_type_list))==True:
						
						if (extension in [".ma", ".mb", ".obj"]) == True:
							destination = os.path.join(destination + "/scenes")
						if (extension in [".png", ".tiff", ".tex", ".exr"]) == True:
							if command == "export":
								destination = os.path.join(destination + "/IMAGES")
							else:
								destination = os.path.join(destination + "/sourceimages")
						if (extension == ".vdb"):
							destination = os.path.join(destination + "/simulation")

						try:
							shutil.copy(origin, destination)
							print("[%s -> %s] Moved" % (origin, destination))
						except:
							mc.warning("[%s -> %s] FAILED" % (origin, destination))
		else:
			mc.error("There is no asset folder, or items inside, or there is nothing to export!")
			return

		


						







	def load_items_type_function(self):
		project = mc.workspace(query=True, rd=True)
		asset_type_selection = mc.textScrollList(self.asset_kind_scrolllist, query=True, si=True)
		asset_folder_selection = mc.textScrollList(self.asset_folder_scrolllist, query=True, si=True)

	

		"""
		take asset folder name(s)
		take asset kind(s)
		depending of the content of the selection
		load items in this folder
		"""
		concerned_assetfolder_files = []
		concerned_project_files = []

		if asset_folder_selection != None:
			for folder in asset_folder_selection:
				for subfolder in os.walk(folder, topdown=True):
					#list all the files
					file_list = subfolder[2]
					if file_list != None:
						for element in file_list:
							if asset_type_selection != None:
								for kind in asset_type_selection:
									if os.path.splitext(element)[1] == kind:
										concerned_assetfolder_files.append(os.path.join(subfolder[0],element))

			mc.textScrollList(self.asset_scrolllist, edit=True, removeAll=True, append=concerned_assetfolder_files)


		if project != None:
			for subfolder in os.walk(project, topdown=True):
					#list all the files
					file_list = subfolder[2]
					if file_list != None:
						for element in file_list:
							if asset_type_selection != None:
								for kind in asset_type_selection:
									if os.path.splitext(element)[1] == kind:
										concerned_project_files.append(os.path.join(subfolder[0],element))
			mc.textScrollList(self.project_scrolllist, edit=True, removeAll=True, append=concerned_project_files)
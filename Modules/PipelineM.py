#coding: utf-8
import maya.cmds as mc
import pymel.core as pm
import os
import ctypes
import sys
import pickle
import json 

from datetime import datetime
from functools import partial







class PipelineApplication:




	def load_settings_function(self):
		if self.project_path == "None":
			mc.error("Impossible to launch settings!")
			return
		else:
		
			if type(self.project_path)==list:
				self.project_path = self.project_path[0]
			try:
				with open(os.path.join(self.project_path, "PipelineManagerData/PipelineSettings.dll"), "rb") as read_file:
					self.settings = pickle.load(read_file)
					self.settings_dictionnary = pickle.load(read_file)
			
			except:
	
				self.settings, self.settings_dictionnary = self.create_pipeline_settings_function()
		return self.settings, self.settings_dictionnary



	def define_default_folder_function(self):
		#define folder
		key_list = list(self.settings.keys())
		selected_key = key_list[int(mc.textScrollList(self.settings_folder_list, query=True, sii=True)[0])-1]
		

		folder = mc.fileDialog2(fm=3)[0]
		if folder == None:
			folder = "None"
		list_content = self.settings[selected_key]
		list_content[2] = folder

		self.settings[selected_key] = list_content

		folder_list = []

		for key, value in self.settings.items():
			if value[2] == None:
				folder_list.append("None")
			else:
				folder_list.append(value[2])

		mc.textScrollList(self.settings_folder_list, edit=True, removeAll=True, append=folder_list)
		#save the new settings folder
		self.save_settings_file()




	def letter_verification_function(self, content):
		letter = "abcdefghijklmnopqrstuvwxyz"
		figure = "0123456789"

		list_letter = list(letter)
		list_capital = list(letter.upper())
		list_figure = list(figure)

		list_content = list(content)
		if list_content == None:
			return False
		for i in range(0, len(list_content)):
			if (list_content[i] in list_letter)==True or (list_content[i] in list_capital)==True or (list_content[i] in list_figure)==True:
				return True
			else:
				if (i == len(list_content) - 1):
					return False




	def define_project_path_ui_function(self, type,event):
		
		if type == "project":
			mc.textField(self.project_label, edit=True, text=mc.workspace(query=True, active=True))
			folder = mc.workspace(query=True, active=True)
		else:
			#open a file explorer to define a folder
			folder = mc.fileDialog2(fm=3)
			if folder == None:
				mc.error("You have to define one folder!")
				return
			else:
				mc.textField(self.project_label, edit=True, text=folder[0])
				#folder = mc.workspace(query=True, active=True)


		with open("data/PipelineData.dll", "wb") as read_file:
			pickle.dump(folder, read_file)

		self.project_path = folder 
		self.reload_settings_function()
		self.shader_init_function()

		self.load_shading_settings_function()
		
		
		self.save_settings_file()
		





	def reload_settings_function(self):
		self.settings, self.settings_dictionnary = self.load_settings_function()



		self.type_list_value = []
		for key, value in self.settings_dictionnary.items():
			self.type_list_value.append(key)

		setting_key_list = []
		setting_value_list = []
		setting_default_folder_list = []
		setting_keyword_list = [] 

		for setting_key, setting_value in self.settings.items():

			#create the default folder buttons
			setting_key_list.append(setting_key)
			setting_value_list.append(setting_value[0])
			setting_keyword_list.append(setting_value[1])

			if setting_value[2] == None:
				setting_default_folder_list.append("None")
			else:
				setting_default_folder_list.append(setting_value[2])



		mc.textScrollList(self.type_list, edit=True, removeAll=True, append=self.type_list_value)
		mc.textScrollList(self.setting_type_list, edit=True, removeAll=True, append=setting_key_list)
		mc.textScrollList(self.setting_syntax_list, edit=True, removeAll=True, append=setting_value_list)
		mc.textScrollList(self.setting_keyword_list, edit=True, removeAll=True, append=setting_keyword_list)
		mc.textScrollList(self.settings_folder_list, edit=True, removeAll=True, append=setting_default_folder_list)

		





	def save_settings_file(self):

		if self.project_path == "None":
			mc.error("Impossible to save the settings file\nYou have to set the pipeline folder first!")
		else:
			if type(self.project_path)==list:
				self.project_path = self.project_path[0]
			if os.path.isdir(os.path.join(self.project_path, "PipelineManagerData"))==False:
				os.mkdir(os.path.join(self.project_path, "PipelineManagerData"))
			
			try:
				with open(os.path.join(self.project_path, "PipelineManagerData/PipelineSettings.dll"), "wb") as save_file:
					pickle.dump(self.settings, save_file)
					pickle.dump(self.settings_dictionnary, save_file)
			except AttributeError:
			
				self.create_pipeline_settings_function()
			self.add_log_content_function("Settings file saved successfully")




	def create_pipeline_settings_function(self):
		basic_file_type_list = ["geo", "rig", "groom", "cloth", "lookdev"]

		#TYPE OF DATA
		#DETECTION OF FILES
		self.settings_dictionnary = {
			"character": basic_file_type_list,
			"prop": basic_file_type_list, 
			"set": basic_file_type_list,
			"fx": "unknown",
			"shots": ["layout", "camera", "anim", "render", "compositing"],
		}
		self.settings = {
			"character":["[project]_[key]_[name]_[type]_[state]", "char", None],
			"prop":["[project]_[key]_[name]_[type]_[state]", "prop", None],
			"set":["[project]_[key]_[name]_[type]_[state]", "set", None],
			"fx":["[project]_[key]_[name]_[type]_[state]","fx", None],
			"shots":["[project]_[key]_[sqversion]_[shversion]_[state]", "shots", None]
		}

		self.save_settings_file()
		return self.settings, self.settings_dictionnary




	def add_log_content_function(self, log_new_content):
		now = datetime.now()
		new_content = "[%s/%s/%s:%s:%s] %s" % (now.year, now.month, now.day, now.hour, now.minute, log_new_content)
		self.log_list_content.append(new_content)

		try:
			mc.textScrollList(self.log_list, edit=True, removeAll=True, append=self.log_list_content)
		except:
			pass




	def add_team_log_content_function(self, log_new_content):
		#get project path
		folder_path = mc.textField(self.project_label, query=True, text=True)
		if os.path.isfile(os.path.join(folder_path, "PipelineManagerData/PipelineManagerTeamLog.dll"))==True:
			#get the content of this file
			try:
				with open(os.path.join(folder_path, "PipelineManagerData/PipelineManagerTeamLog.dll"), "rb") as read_file:
					team_content = pickle.load(read_file)
				#get the old content
			except:
				mc.error("Impossible to change the team log file!")
				return 
			else:
				if type(team_content)==list:
					
					
					team_content.append(log_new_content)
					with open(os.path.join(folder_path, "PIpelineManagerData/PipelineManagerTeamLog.dll"), "wb") as save_file:
						pickle.dump(team_content, save_file)





	def display_new_list_function(self):

		"""
		check the selection of all list to create the content of the next one
		if you change the previous one check if the content of the next list need to change
		if it does, change it (obvious bro)
		"""
		type_selection = mc.textScrollList(self.type_list, query=True, si=True)
		kind_selection = mc.textScrollList(self.kind_list, query=True, si=True)
		name_selection = mc.textScrollList(self.name_list, query=True, si=True)

		
		
		if type_selection != None:
			past_type_list = self.new_type_list 
			self.new_type_list = []

			for element in type_selection:
				for key, value in self.settings_dictionnary.items():
					if key == element:
						if type(value) != list:
							value = [value]
						for item in value:
							if (item in self.new_type_list)==False:
								self.new_type_list.append(item)
			if (past_type_list != self.new_type_list):
				mc.textScrollList(self.kind_list, edit=True, removeAll=True, append=self.new_type_list)


		#add content to next list
		"""
		if step_selection != None:
			past_step_list = self.new_step_list
			self.new_step_list = []

			for element in step_selection:
				for key, value in self.settings_dictionnary.items():
					if element == key:
						
						for value_key, value_value in value.items():
							if (value_key in self.new_step_list)==False:
								self.new_step_list.append(value_key)

			if (past_step_list != self.new_step_list):
				mc.textScrollList(self.type_list, edit=True, removeAll=True, append=self.new_step_list)
				mc.textScrollList(self.kind_list, edit=True, removeAll=True)"""


		"""
		if type_selection != None:
			past_type_list = self.new_type_list
			self.new_type_list = []

			for element in type_selection:
				for key, value in self.settings_dictionnary.items():
					#create categorie list	
					for value_key, value_value in value.items():
						if value_key == element:
							if type(value_value) != list:
								value_value = [value_value]
							for item in value_value:
								if (item in self.new_type_list)==False:
									self.new_type_list.append(item)"""


			

		self.search_files_function(type_selection, kind_selection, name_selection)




	def search_files_function(self, type_selection, kind_selection, name_selection):
		"""
		check the selection in all lists
		check the content
		"""
		#do a recurcive selection
		#go from the step_list to take files recurcively column after column
		files_in_folder = []


		past_name_list = self.name_list_value
		self.result_list_value = []
		self.name_list_value = []


		folder_name = (mc.textField(self.project_label, query=True, text=True))
		project_name = os.path.basename(os.path.normpath(folder_name))


		for r, d, f in os.walk(folder_name):
			for file in f:
				files_in_folder.append(os.path.join(r, file))
		
		
		#splited_file = os.path.splitext(os.path.basename(file))[0].split("_")
		
		

		if type_selection != None:
			#print("_____________________________________________________")
			for ts in type_selection:
				for file in files_in_folder:
					error=False
					name = None
					#get the setting and the syntax linked to it
					syntax = self.settings[ts][0]
					keyword = self.settings[ts][1]

					#check the syntax for each files
					#CHECK FIRST THE TYPE OF THE FILE (INCLUDING THE OVERHALL SYNTAX!!!")
					splited_syntax = syntax.split("_")
					splited_file = os.path.splitext(os.path.basename(file))[0].split("_")


					if self.letter_verification_function(syntax) == False:
						mc.warning("Impossible to search for files because no syntax to search!")
						error = True



					elif len(splited_syntax) != len(splited_file):
						error = True


					else:
						for i in range(0, len(splited_syntax)):
							#check each keyword
							#store the name after the control!!!
							if splited_syntax[i] == "[key]":
								if splited_file[i] != keyword:
									error=True
							elif splited_syntax[i] == "[project]":
								if splited_file[i] != project_name:
									error=True
							elif splited_syntax[i] == "[state]":
								if (splited_file[i] in ["edit", "publish"])==False:
									error=True
							elif splited_syntax[i] == "[type]":
								if kind_selection != None:
									if (splited_file[i] in kind_selection)==False:
										error=True
							elif splited_syntax[i] == "[version]":
								splited = splited_file[i].split("v")
								if len(splited) != 2:
									if (splited[0] != "") or (splited[1].isnumeric())==False:
										error=True
							elif splited_syntax[i] == "[name]":
								name = splited_file[i]
							elif splited_syntax[i] == "[shversion]":
								splited = splited_file[i].split("sh")
								if len(splited)!=2:
									error=True
								else:
									if (splited[0]!="") or (splited[0].isdigit())==False:
										error=True
							elif splited_syntax[i] == "[sqversion]":
								splited = splited_file[i].split("sq")
								if len(splited)!=2:
									error=True
								else:
									if (splited[0]!="") or (splited[0].isdigit())==False:
										error=True
							
							else:
								#check if the syntax item is the same item in the filename
								#it mean that no variable was use in the syntax field
								if splited_syntax[i] != splited_file[i]:
									error=True
					if error==False:
						"""
						detect if a name is detected in the name selection
						if one or several names are detected, check if the file name is contained in the list

							-> if yes -> add the file
							-> if not -> don't
							-> if there is no name detected in the selection add the file anyway
						"""
						
						if name != None:
							self.name_list_value.append(name)


						if name_selection != None:
							if (name != None) and (name in name_selection)==True:
								self.result_list_value.append(file)
						if name_selection == None:
							self.result_list_value.append(file)
						"""
						if name != None:
							self.name_list_value.append(name)
						
						self.result_list_value.append(file)"""


		for i in range(0, len(self.result_list_value)):
			self.result_list_value[i] = (os.path.basename(self.result_list_value[i]))

		mc.textScrollList(self.result_list, edit=True, removeAll=True, append=self.result_list_value)
		
		if past_name_list != self.name_list_value:	
			mc.textScrollList(self.name_list, edit=True, removeAll=True, append=self.name_list_value)

								


	def save_new_syntax_function(self, event):
		#check selection of the textscrolllist
		selection = mc.textScrollList(self.setting_syntax_list, query=True, sii=True)
		new_content = mc.textField(self.setting_syntax_textfield, query=True, text=True)

		if (self.letter_verification_function(new_content)==None) or (self.letter_verification_function(new_content)==False):
			mc.error("You have to write a new syntax to replace the old one!")
			return
		if selection == None:
			mc.error("You have at least one setting to change!")
			return 
		else:
			#get list of informations from settings dictionnary
			keys = list(self.settings.keys())
			values = list(self.settings.values())

			for rank in selection:
				for i in range(0, len(keys)):
					#check if at the specified rank
					if (int(rank)-1) == i:
						self.add_log_content_function("[%s] New syntax has been saved" % keys[i])
						values[i][0] = new_content
			for i in range(0, len(keys)):
				self.settings[keys[i]] = values[i]

			self.save_settings_file()

			new_values = []
			for value in values:
				new_values.append(value[0])
			mc.textScrollList(self.setting_syntax_list, edit=True, removeAll=True, append=new_values)
			self.deselect_all_lists()



	def deselect_all_lists(self):
		mc.textScrollList(self.type_list, edit=True, deselectAll=True)
		mc.textScrollList(self.name_list, edit=True, deselectAll=True)
		mc.textScrollList(self.kind_list, edit=True, deselectAll=True)
		mc.textScrollList(self.result_list, edit=True, deselectAll=True)



	def reset_default_syntax_function(self,event):
		self.delete_settings_interface_item_function()
		self.default_settings = {
			"character":["[project]_[key]_[name]_[type]_[state]", "char", None],
			"prop":["[project]_[key]_[name]_[type]_[state]", "prop", None],
			"set":["[project]_[key]_[name]_[type]_[state]", "set", None],
			"fx":["[project]_[key]_[name]_[type]_[state]","fx", None],
			"shots":["[project]_[key]_[sqversion]_[shversion]_[state]", "shots", None]
		}
		basic_file_type_list = ["geo", "rig", "groom", "cloth", "lookdev"]

		#TYPE OF DATA
		#DETECTION OF FILES
		self.default_settings_dictionnary = {
			"character": basic_file_type_list,
			"prop": basic_file_type_list, 
			"set": basic_file_type_list,
			"fx": "unknown",
			"shots": ["layout", "camera", "anim", "render", "compositing"],
		}

		selection = mc.textScrollList(self.setting_syntax_list, query=True, sii=True)
		if selection == None:
			self.settings = self.default_settings
			self.settings_dictionnary = self.default_settings_dictionnary
			self.save_settings_file()
		else:
			for i in range(0, len(selection)):
				selection[i] = int(selection[i]) - 1
			old_values = list(self.default_settings.values())
			keys = list(self.settings.keys())

			for rank in selection:
				for i in range(0, len(keys)):
					if int(rank) == i:
						self.add_log_content_function("[%s] Setting has been reset"%keys[i])
						self.settings[keys[i]] = old_values[i]

			self.save_settings_file()

			values = list(self.settings.values())
			keys = list(self.settings.keys())

			for i in range(0, len(values)):
				values[i] = values[i][0]

		self.create_settings_interface_item_function()



	def import_in_scene_function(self, command, event):
		#get the selection in the file list
		file_selection = mc.textScrollList(self.result_list, query=True, si=True)
		folder_name = (mc.textField(self.project_label, query=True, text=True))
		#project_name = os.path.basename(os.path.normpath(folder_name))

		if file_selection == None:
			mc.error("You have to select at least one file!")
			return 



		#try to find file in the folder
		for item in file_selection:
			for r, d, f in os.walk(folder_name):
				for file in f:
					if file == item:
						self.add_log_content_function("[%s] File found in project" % item)
						if os.path.isfile(os.path.join(r, item)):
							try:
								if command==False:
									mc.file(os.path.join(r, item), i=True)
								if command==True:
									mc.file(os.path.join(r, item), r=True)
								self.add_log_content_function("[%s] File imported successfully"%item)
							except:
								mc.error("Impossible to import file!")
								return

			


	def clean_function(self, event):
		nodes_list = mc.ls(st=True)
		node_name = []
		node_type = []

		for i in range(0, len(nodes_list)):
			if i%2 == 0:
				node_name.append(nodes_list[i])
			else:
				node_type.append(nodes_list[i])
		#for each node check its connection
		for item in node_name:
			print(mc.listConnections(item))




	def save_new_scene_function(self, event):
		#get fields / checkbox ... values to create the new file
		"""
		CHECK THE NOMENCLATURE

		check that the name isn't empty, if the name is empty keep filename
		check if there is a defined folder for the kind, if not ask to define it
		check the version (add zeros in the version number)
		add if edit if [state] keyword is in the nomenclature
		"""
		new_filename = []

		#get the nomenclature of the file according to the chosen kind
		folder_name = (mc.textField(self.project_label, query=True, text=True))
		project_name = os.path.basename(os.path.normpath(folder_name))
		kind_selection = mc.optionMenu(self.export_kind_menu, query=True, value=True)
		version_selection = int(mc.intField(self.export_version_intfield, query=True, value=True))
		type_selection = mc.optionMenu(self.export_type_menu, query=True, value=True)
		extension_selection = mc.optionMenu(self.export_extension_menu, query=True, value=True)
		shot_version_selection = mc.intField(self.shot_version_intfield, query=True, value=True)
		sequence_version_selection = mc.intField(self.sequence_version_intfield, query=True, value=True)



		syntax = self.settings[kind_selection][0]
		keyword = self.settings[kind_selection][1]

		splited_syntax = syntax.split("_")


		for i in range(0, len(splited_syntax)):
			if splited_syntax[i] == "[key]":
				new_filename.append(keyword)
			elif splited_syntax[i] == "[project]":
				new_filename.append(project_name)
			elif splited_syntax[i] == "[name]":
				"""
				check the content of the textfield
				put this in the syntax list
				"""
				content = mc.textField(self.export_name_textfield, query=True, text=True)
				if (self.letter_verification_function(content)==False) and (self.letter_verification_function(content)==None):
					mc.error("You have to define a name!")
					return
				else:
					new_filename.append(content)
			elif splited_syntax[i] == "[type]":
				new_filename.append(type_selection)
			elif splited_syntax[i] == "[state]":
				new_filename.append("edit")

			elif (splited_syntax[i] == "[shversion]") or (splited_syntax[i] == "[sqversion]") or (splited_syntax[i] == "[version]"):
				print(splited_syntax[i])
				"""
				creation of the version list
				"""
				if splited_syntax[i] == "[shversion]":
					version_input = shot_version_selection
				if splited_syntax[i] == "[sqversion]":
					version_input = sequence_version_selection
				if splited_syntax[i] == "[version]":
					version_input = version_selection

				if version_input < 100:
					version_list = list(str(version_input))

					while len(version_list) != 3:
						version_list.insert(0, 0)
				else:
					version_list = list(str(version_input))
					version_list.insert(0, 0)

				for y in range(0, len(version_list)):
					version_list[y] = str(version_list[y])
				
				if splited_syntax[i] == "[shversion]":
					new_filename.append("sh"+"".join(version_list))
				if splited_syntax[i] == "[sqversion]":
					new_filename.append("sq"+"".join(version_list))
				if splited_syntax[i] == "[version]":
					new_filename.append("".join(version_list))

			else:
				#add the content of the syntax in the list anyway
				#it mean that this content isn't a syntax variable
				new_filename.append(splited_syntax[i])


				
		#create the final name
		filename = "_".join(new_filename)+(extension_selection)
		#check the value of the "default folder checkbox"
		#if the value is true, check if there is a default folder
		#	if yes --> use it
		#
		#else ask where to put the file
		default_folder_checkbox_value = mc.checkBox(self.export_use_default_folder_checkbox, query=True, value=True)
		default_folder = None

		if default_folder_checkbox_value == True:
			#get the default folder
			if self.settings[kind_selection][2] != None:
				default_folder = self.settings[kind_selection][2]
			else:
				mc.warning("No default folder is defined for this kind!")
		if default_folder == None:
			try:
				default_folder = mc.fileDialog2(fm=3)[0]
			except:
				mc.error("You have to define a default folder!")
				self.add_log_content_function("Edit file export failed")
				return
		#create the new file
		filename = os.path.join(default_folder, filename)
		if mc.checkBox(self.export_save_previous_scene_checkbox, query=True, value=True)==True:
			mc.file(save=True)
		mc.file(rename=filename)
		mc.file(save=True)


		#write new content for the team log file
		dt = datetime.today()
		self.add_team_log_content_function("[%s:%s:%s] New edit file saved | %s |"%(dt.year, dt.month, dt.day, filename))
		self.add_log_content_function("New edit file saved - [%s]"%filename)



	def delete_type_function(self, event):
		#get the value in the type textscrolllist
		type_list = mc.textScrollList(self.setting_type_list, query=True, si=True)

		if type_list == None:
			mc.error("You have to select at least one type to delete!")
			return

		else:
			self.delete_settings_interface_item_function()
			for item in type_list:
				#delete the corresponding key in the dictionnary
				self.settings.pop(item)
			
			self.create_settings_interface_item_function()
			self.save_settings_file()



	def create_type_function(self, event):
		"""
		take the content of the type name textfield / setting syntax textfield
		and create a new setting

		if there is no content in the syntax field put "" in the syntax
		#so the program will detect that it's impossible to search for file
		"""
		setting_name_content = mc.textField(self.settings_create_type_textfield, query=True, text=True)
		setting_syntax_content = mc.textField(self.setting_syntax_textfield, query=True, text=True)
		setting_keyword_content = mc.textField(self.settings_create_keyword_textfield, query=True, text=True)

		if (self.letter_verification_function(setting_name_content)==False) or (self.letter_verification_function(setting_name_content)==None) or (self.letter_verification_function(setting_keyword_content)==False) or (self.letter_verification_function(setting_keyword_content)==None):
			mc.error("You have to define a name and a keyword to create a new type!")
			return

		if (self.letter_verification_function(setting_syntax_content)==False) or (self.letter_verification_function(setting_syntax_content)==None):
			mc.warning("No setting saved with the new type!")
			setting_syntax_content = ""

		if (setting_name_content in self.settings)==True:
			mc.error("An existing type with the same name already exist!")
			return
		else:
			#delete all the buttons on the GUI
			#self.delete_button_function()
			#create the new key in the dictionnary
			self.delete_settings_interface_item_function()
			self.settings[setting_name_content] = [setting_syntax_content, setting_keyword_content, None]
			self.save_settings_file()
			self.create_settings_interface_item_function()



	def save_keyword_function(self, event):
		try:
			selection = mc.textScrollList(self.setting_keyword_list, query=True, sii=True)[0]
		except TypeError:
			mc.error("You have to select one keyword to change in the list!")
			return
		content = mc.textField(self.settings_create_keyword_textfield, query=True, text=True)

		#check if the content contain something
		if (self.letter_verification_function(content)==False) or (self.letter_verification_function(content)==None):
			mc.error("You have to define a new keyword!")
			return
		keyword_exist = False
		for key, value in self.settings.items():
			if value[1] == content:
				keyword_exist = True
		if keyword_exist == True:
			mc.error("This keyword is already taken!")
			return
		else:
			self.delete_settings_interface_item_function()
			#change the value in the dictionnary
			keys = list(self.settings.keys())
			values = list(self.settings.values())

			for i in range(0, len(keys)):
				if i == (int(selection) - 1):
					self.settings[keys[i]] = [values[i][0], content, values[i][2]]	
			#save the new dictionnary
			self.save_settings_file()
			self.create_settings_interface_item_function()









	






	

		

				



				






		




		
						


		

		

							

		
		
		

		
			

















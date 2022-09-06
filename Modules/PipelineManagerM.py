#coding: utf-8
#PIPELINE MANAGER

#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
import threading
import maya.cmds as mc
import pymel.core as pm
import os  
import ctypes
import sys
import pickle

from time import sleep
from functools import partial
from datetime import datetime




"""

def onMayaDroppedPythonFile(*args):
	#create the path for all the functions
	path = '/'.join(__file__.replace("", "/").split("/")[:-1])
	sys.path.append(path)
	"""



"""
check if project list exists
	add project to list
		when the program launch check if program exists
	if project doesn't exist don't load them

"""



"""

TASKLIST	
	- import in current scene*
	- import as reference in current scene*
	

	- create a log for the local program*
	- create a general log for the whole project (located directly in the pipeline)
	- create a tasklist file for the whole project (located directly in the pipeline)

"""
"""


try:
	from PyToolBar_03.Modules.PipelineM import PipelineApplication
	from PyToolBar_03.Modules.PipelineShaderM import PipelineShaderApplication

except:
	mc.error("Pipeline Module not found or impossible to import!")
	sys.exit()"""




class PipelineGuiApplication():
#class PipelineGuiApplication():







	
	def resize_command_function(self):
		#get the window width
		width = mc.window(self.main_window, query=True, width=True)
		height= mc.window(self.main_window, query=True, height=True)

		
		#MAIN FRAME
		mc.frameLayout(self.PipelineManagerTool, edit=True, width=width)

		#HOME PAGE
		mc.frameLayout(self.assets_search_frame, edit=True, width=width)
		mc.rowColumnLayout(self.prod_columns, edit=True, columnWidth=((1, width/5), (2, width/5), (3, width/5), (4, width/5)))
		mc.rowColumnLayout(self.import_rowcolumn, edit=True, columnWidth=((1, width/2), (2, width/2)))

		mc.frameLayout(self.texture_search_frame, edit=True, width=width)
		mc.rowColumnLayout(self.texture_columns, edit=True, columnWidth=((1, width/4),(2, width/4),(3, width/4)))

		#EXPORT PAGE
		mc.frameLayout(self.export_frame, edit=True, width=width)
		mc.rowColumnLayout(self.export_save_rowcolumn, edit=True, columnWidth=((1, width/5), (2, width/5), (3, width/5), (4, width/5), (5, width/5)))
		mc.rowColumnLayout(self.export_version_rowcolumn, edit=True, columnWidth=((1, width/20), (2, width/5)))
		mc.rowColumnLayout(self.export_shot_version_rowcolumn, edit=True, columnWidth=((1, width/2), (2, width/2)))
		mc.rowColumnLayout(self.final_export_rowcolumn, edit=True, columnWidth=((1, width/3), (2, width/3), (3, width/3)))

		#SETTINGS PAGE
		mc.frameLayout(self.settings_file_frame, edit=True, width=width)
		mc.rowColumnLayout(self.setting_rowcolumn1, edit=True, columnWidth=((1, width/6), (2, width/6), (3, width/6), (4, width/2)))
		mc.rowColumnLayout(self.setting_rowcolumn2, edit=True, columnWidth=((1, width/2), (2, width/2)))
		mc.rowColumnLayout(self.setting_rowcolumn2button, edit=True, columnWidth=((1, width/3), (2, width/3), (3, width/3)))
		mc.rowColumnLayout(self.setting_rowcolumn3, edit=True, width=width,columnWidth=((1, width/2-10), (2, width/4-10), (3,width/4-10)))

		mc.frameLayout(self.settings_texture_frame, edit=True, width=width)
		mc.rowColumnLayout(self.shading_settings_rowcolumn1, edit=True, columnWidth=((1, width/4), (2, int(width - width/4))))
		mc.rowColumnLayout(self.shading_settings_rowcolumn2, edit=True, columnWidth=((1, width/4), (2, width/4), (3, width/4)))
		mc.rowColumnLayout(self.shading_settings_rowcolumn3, edit=True, columnWidth=((1, width/4), (2, width/4), (3, width/4)))
		mc.rowColumnLayout(self.shading_settings_rowcolumn4, edit=True, columnWidth=((1, int(width-width/4)/2), (2, int(width-width/4)/2)))
		mc.rowColumnLayout(self.channel_editor_rowcolumnlayout, edit=True, columnWidth=((1, width/2), (2, width/2)))
		#LOG PAGE
		mc.frameLayout(self.log_program_frame, edit=True, width=width)
		mc.frameLayout(self.log_team_frame, edit=True, width=width)





	
	def main_message_thread_function(self):
		self.launch_message_thread = True
		self.continue_message_thread = True
		i = 0

		while self.continue_message_thread == True:
			window_exist = mc.window(self.main_window, query=True, exists=True)
			if window_exist == False:
				self.continue_message_thread = False
				break 
			
			else:
				
				#check if the file exist
				#if it doesn't do nothing
				#if the file exist, read it
				#and add the list in the team logs textscrolllist

				#get project path
				folder = mc.textField(self.project_label, query=True, text=True)
				if os.path.isfile(os.path.join(folder, "PipelineManagerData/PipelineManagerTeamLog.dll"))==True:
					
					#try to read the content of the file
					#add this content (if its a list) to the textscrolllist in the team logs menu
					try:
						with open(os.path.join(folder, "PipelineManagerData/PipelineManagerTeamLog.dll"), "rb") as read_file:
							team_log_data = pickle.load(read_file)
					except:
						#delete the file and create a new log
						mc.error("Error - The team log is corrupted!")
						os.remove(os.path.join(folder, "PipelineManagerData/PipelineManagerTeamLog.dll"))
						mc.warning("The file will be recreated!")
					else:
						if type(team_log_data)==list:
							#create the new notification
							if len(team_log_data) != 1:
								notification = team_log_data[-1]

								if len(team_log_data) != len(self.previous_log_team):
									self.previous_log_team = team_log_data
									if i != 0:
										
										mc.inViewMessage(amg="New team log notification\n[%s]"%notification, pos="midCenter", fade=True)
										mc.warning("New team log notification | %s"%notification)
										sleep(3)
									#create the new notification
									mc.textScrollList(self.lost_team_list, edit=True, removeAll=True, append=team_log_data)	
						"""		
						if type(team_log_data)==list:
							#get the content of the previous list
							#check if there is a difference
							if team_log_data != self.previous_log_team:
								mc.textScrollList(self.lost_team_list, edit=True, removeAll=True, append=team_log_data)
								self.previous_log_team = team_log_data
								notification = team_log_data[-1]
								#mc.inViewMessage(amg="New team log notification<br/><h1>%s</h1>"%notification, pos="midCenter", fade=True)
								"""
							
	
				#create a new log file
				else:
					
					
					#get the date and the time
					dt = datetime.today()

					new_log = [
						"Log creation [%s:%s:%s]"%(dt.year, dt.month, dt.day)
						]
					if folder != "None":
						if os.path.isdir(os.path.join(folder, "PipelineManagerData"))==False:
							os.mkdir(os.path.join(folder, "PipelineManagerData"))
						with open(os.path.join(folder, "PipelineManagerData/PipelineManagerTeamLog.dll"), "wb") as save_file:
							pickle.dump(new_log, save_file)
						mc.warning("Team log file created")
					
			sleep(1)
			i+=1
			
	
		







	def build_pipeline_interface_function(self):
		self.add_log_content_function("Interface builded")
		#self.main_window = mc.window(title="PipelineManager", sizeable=True, height=self.window_height, width=self.window_width)
		self.pack_function_list["Pipeline"] = ["PipelineManagerTool"]


		#self.main_column = mc.columnLayout(adjustableColumn=True)
		self.PipelineManagerTool = mc.frameLayout(visible=False, parent=self.main_column, label="PipelineManagerTool", labelAlign="top", width=self.window_width, collapsable=True, collapse=True, backgroundColor=(0.921,0.596,0.305))

		self.form_pipeline = mc.formLayout(parent=self.PipelineManagerTool)
		self.tabs = mc.tabLayout(innerMarginWidth=5, innerMarginHeight=5, parent=self.form_pipeline)
		mc.formLayout(self.form_pipeline, edit=True, attachForm=((self.tabs,"top",0), (self.tabs, "bottom",0),(self.tabs,"left",0),(self.tabs,"right",0)))

		"""
		ASSETS
		character, props, sets, fx
		mod, rig, groom, cloth, lookdev, alembic
		
		SHOTS
		sequence, shots
		layout, camera, matte painting, anim, render

		POSTPROD
		sequence, shots
		renders, compositing
		"""
		#main scroll layout of the asset page
		self.prod_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)
		self.asset_main_scroll = mc.scrollLayout(horizontalScrollBarThickness=1, width=self.window_width+16, parent=self.prod_column, resizeCommand=self.resize_command_function, height=self.window_height)
		


		#DEFINE PROJECT FOLDER
		mc.separator(style="none", height=15, parent=self.asset_main_scroll)

		
		self.project_columns = mc.rowColumnLayout(numberOfColumns=3, parent=self.asset_main_scroll, columnWidth=((1, self.window_width/2)))
		self.project_label = mc.textField(editable=False, backgroundColor=[0.2, 0.2, 0.2], parent=self.project_columns, text=self.project_path)
		mc.button(label="Set Project Folder", parent=self.project_columns, command=partial(self.define_project_path_ui_function, "project"))
		mc.button(label="Set Other Folder", parent=self.project_columns, command=partial(self.define_project_path_ui_function, "folder"))
		mc.separator(style="singleDash", height=25, parent=self.asset_main_scroll)


		self.assets_search_frame = mc.frameLayout(label="Search for assets", parent=self.asset_main_scroll, collapsable=True, collapse=True, width=self.window_width)
		self.prod_scroll = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.assets_search_frame,height=self.window_height/2)	
		self.prod_columns = mc.rowColumnLayout(numberOfColumns=5 , columnWidth=((1, self.window_width/5), (2, self.window_width/5),(3, self.window_width/5), (4, self.window_width/5)),parent=self.prod_scroll)

		mc.text(label="Kind", parent=self.prod_columns, align="left")
		mc.text(label="Name", parent=self.prod_columns, align="left")
		mc.text(label="File Type", parent=self.prod_columns, align="left")
		mc.text(label="Files Found", parent=self.prod_columns, align="left")
		mc.text(label="", parent=self.prod_columns)


		#create textscrolllist lists
		if self.project_path !="None":
			for key, value in self.settings_dictionnary.items():
		
				self.type_list_value.append(key)

		self.type_list = mc.textScrollList(allowMultiSelection=True, parent=self.prod_columns, height=self.window_height/2, selectCommand=self.display_new_list_function, append=self.type_list_value)
		self.name_list = mc.textScrollList(allowMultiSelection=True, parent=self.prod_columns, height=self.window_height/2, selectCommand=self.display_new_list_function)
		self.kind_list = mc.textScrollList(allowMultiSelection=True, parent=self.prod_columns, height=self.window_height/2, selectCommand=self.display_new_list_function)
		self.result_list = mc.textScrollList(allowMultiSelection=True, parent=self.prod_columns, height=self.window_height/2)
		#self.result_scrollbar = mc.scrollLayout(parent=self.result_list, sah=False, horizontalScrollBarThickness=16)

		#IMPORT FILES
		mc.separator(parent=self.assets_search_frame, style="none", height=30)
		self.import_rowcolumn = mc.rowColumnLayout(parent=self.assets_search_frame, numberOfColumns=2, columnAlign=((1, "left"), (2, "right")), columnWidth=((1, self.window_width/2), (2, self.window_width/2)))
		mc.button(label="Import in scene", parent=self.import_rowcolumn, command=partial(self.import_in_scene_function, False))
		mc.button(label="Import as reference", parent=self.import_rowcolumn, command=partial(self.import_in_scene_function, True))	








		self.texture_search_frame = mc.frameLayout(label="Search for textures", width=self.window_width, parent=self.asset_main_scroll, collapsable=True, collapse=False)
		self.texture_scroll_layout = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.texture_search_frame, height=1)	

		#texture path field
		self.texture_path_row_columns = mc.rowColumnLayout(numberOfColumns=2, parent=self.texture_search_frame, columnWidth=((1, self.window_width/2), (2, self.window_width/2)))
		mc.text(label="Texture folder path", parent=self.texture_path_row_columns)
		mc.text(label="", parent=self.texture_path_row_columns)
		self.texture_path_field = mc.textField(text=self.texture_folder_path, parent=self.texture_path_row_columns, editable=False, backgroundColor=[0.2, 0.2, 0.2])
		mc.button(label="Define an other folder", parent=self.texture_path_row_columns, command=self.define_other_texture_folder_function)


		self.texture_columns = mc.rowColumnLayout(parent=self.texture_search_frame, numberOfColumns=3, width=self.window_width, columnWidth=((1, self.window_width/3), (2, self.window_width/3), (3, self.window_width/3)))


		mc.text(label="Channel", parent=self.texture_columns)
		mc.text(label="Name", parent=self.texture_columns)
		mc.text(label="Files Found", parent=self.texture_columns)

		self.texture_channel_list = mc.textScrollList(allowMultiSelection=False, parent=self.texture_columns, height=self.window_height/2, selectCommand=partial(self.refresh_textures_list_function, "channel"))
		self.texture_name_list = mc.textScrollList(allowMultiSelection=True, parent=self.texture_columns, height=self.window_height/2, selectCommand=partial(self.refresh_textures_list_function, "name"))
		self.texture_found_list = mc.textScrollList(allowMultiSelection=False, parent=self.texture_columns, height=self.window_height/2, selectCommand=self.select_texture_function)

		self.texture_shader_connexion_column = mc.rowColumnLayout(numberOfColumns=2, parent=self.texture_search_frame, columnWidth=((1, self.window_width/2), (2, self.window_width/2)))
		mc.button(label="Create Shader", parent=self.texture_shader_connexion_column, command=self.create_pipeline_shader_function)
		mc.button(label="Use existing Shader", parent=self.texture_shader_connexion_column, command=self.use_existing_shader_function)













		self.export_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)
		self.export_scroll = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.export_column, height=self.window_height, resizeCommand=self.resize_command_function)
		self.export_frame = mc.frameLayout(label="Save new edit file", width=self.window_width, parent=self.export_scroll, collapse=True, collapsable=True)
		"""
		save a new scene
		publish the scene
			version
			extension
			destination
			type
			name
				CALL THE NOMENCLATURE SETTINGS NO NAME THE FILE

			clean tool
				import refs
				delete all namespaces
				export this file as a new file (publish file)

				IF RIGGING
					delete unused nodes
					check position of all controllers
					sks hidden?
					(check gesse documentation)

				delete volume aggregates from renderman if there is volume aggregates

		"""
		self.export_save_rowcolumn = mc.rowColumnLayout(numberOfColumns=5, parent=self.export_frame, columnWidth=((1, self.window_width/5), (2, self.window_width/5),(3, self.window_width/5),(4, self.window_width/5), (5,self.window_width/5)))

		mc.text(label="Name", parent=self.export_save_rowcolumn)
		mc.text(label="Kind", parent=self.export_save_rowcolumn)
		mc.text(label="Version", parent=self.export_save_rowcolumn)
		mc.text(label="Type", parent=self.export_save_rowcolumn)
		mc.text(label="Extension", parent=self.export_save_rowcolumn)

		self.export_name_textfield = mc.textField(parent=self.export_save_rowcolumn)

		self.export_kind_menu = mc.optionMenu(parent=self.export_save_rowcolumn)

		for key in self.settings:
			mc.menuItem(label=key)
	
		self.export_version_rowcolumn = mc.rowColumnLayout(numberOfColumns=2, parent=self.export_save_rowcolumn, columnWidth=((1, self.window_width/20), (2, self.window_width/5)))
		mc.text(label="V", parent=self.export_version_rowcolumn)
		self.export_version_intfield = mc.intField(parent=self.export_version_rowcolumn, minValue=0)

		self.export_type_menu = mc.optionMenu(parent=self.export_save_rowcolumn)
		for item in self.file_type:
			mc.menuItem(label=item)

		self.export_extension_menu = mc.optionMenu(parent=self.export_save_rowcolumn)
		mc.menuItem(label=".ma")
		mc.menuItem(label=".mb")

		self.export_shot_version_rowcolumn = mc.rowColumnLayout(numberOfColumns=2, parent=self.export_frame, columnWidth=((1, self.window_width/2), (2, self.window_width/2)))
		mc.text(label="Shot version", parent=self.export_shot_version_rowcolumn)
		mc.text(label="Sequence version", parent=self.export_shot_version_rowcolumn)
		self.sequence_version_intfield = mc.intField(parent=self.export_shot_version_rowcolumn, minValue=0)
		self.shot_version_intfield = mc.intField(parent=self.export_shot_version_rowcolumn, minValue=0)
		
		self.final_export_rowcolumn = mc.rowColumnLayout(numberOfColumns=3, parent=self.export_frame, columnWidth=((1, self.window_width/3), (2, self.window_width/3), (3, self.window_width/3)))
		self.export_use_default_folder_checkbox = mc.checkBox(label="Use default folder", parent=self.final_export_rowcolumn, value=False)
		self.export_save_previous_scene_checkbox = mc.checkBox(label="Save actual scene", parent=self.final_export_rowcolumn, value=False)
		mc.button(label="Save new scene", parent=self.final_export_rowcolumn, command=self.save_new_scene_function)








		self.settings_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)
		#create two list (left and right)
		#LEFT --> NAME OF THE SETTING
		#RIGHT --> VALUE OF THE SYNTAX
		self.settings_main_scroll = mc.scrollLayout(horizontalScrollBarThickness=1, parent=self.settings_column, resizeCommand=self.resize_command_function, width=self.window_width,height=self.window_height)

		self.settings_file_frame = mc.frameLayout(label="Files settings", parent=self.settings_main_scroll, width=self.window_width, collapsable=True, collapse=True)
		self.settings_file_scroll = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.settings_file_frame, height=self.window_height/2)
		self.setting_rowcolumn1 = mc.rowColumnLayout(numberOfColumns=4, parent=self.settings_file_scroll, columnWidth=((1, self.window_width/6), (2, self.window_width/6), (3, self.window_width/6), (4, self.window_width/2)))
		mc.text(label="Type name", parent=self.setting_rowcolumn1)
		mc.text(label="Type syntax", parent=self.setting_rowcolumn1)
		mc.text(label="Type keyword", parent=self.setting_rowcolumn1)
		mc.text(label="Type default folder", parent=self.setting_rowcolumn1)

		#create the setting key list
		setting_key_list = []
		setting_value_list = []
		setting_default_folder_list = []
		setting_keyword_list = []


		for setting_key, setting_value in self.settings.items():
			setting_key_list.append(setting_key)
			setting_value_list.append(setting_value[0])
			setting_keyword_list.append(setting_value[1])

			if setting_value[2] == None:
				setting_default_folder_list.append("None")
			else:
				setting_default_folder_list.append(setting_value[2])

		self.setting_type_list = mc.textScrollList(allowMultiSelection=True, parent=self.setting_rowcolumn1, append=setting_key_list)
		self.setting_syntax_list = mc.textScrollList(allowMultiSelection=False, parent=self.setting_rowcolumn1, append=setting_value_list, selectCommand=self.add_content_in_textfield_function)
		self.setting_keyword_list = mc.textScrollList(allowMultiSelection=False, parent=self.setting_rowcolumn1, append=setting_keyword_list)
		self.settings_folder_list = mc.textScrollList(allowMultiSelection=False, parent=self.setting_rowcolumn1, append=setting_default_folder_list, selectCommand=self.define_default_folder_function)


		self.setting_rowcolumn2 = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width/2), (2, self.window_width/2)), parent=self.settings_file_scroll)
		
		mc.text(label="New type name", parent=self.setting_rowcolumn2)
		mc.text(label="New type keyword", parent=self.setting_rowcolumn2)
		self.settings_create_type_textfield = mc.textField(parent=self.setting_rowcolumn2)
		self.settings_create_keyword_textfield = mc.textField(parent=self.setting_rowcolumn2)

		self.setting_rowcolumn2button = mc.rowColumnLayout(numberOfColumns=3, parent=self.settings_file_scroll, columnWidth=((1, self.window_width/3), (2, self.window_width/3), (3, self.window_width/3)))
		
		mc.button(label="Save\nkeyword", parent=self.setting_rowcolumn2button, command=self.save_keyword_function)
		mc.button(label="Create\nnew type", parent=self.setting_rowcolumn2button, command=self.create_type_function)
		mc.button(label="Delete type", parent=self.setting_rowcolumn2button, command=self.delete_type_function)


		self.setting_rowcolumn3 = mc.rowColumnLayout(numberOfColumns=3, parent=self.settings_file_scroll, width=self.window_width, columnWidth=((1, self.window_width/2-10), (2, self.window_width/4-10), (3, self.window_width/4-10)))
		mc.text(label="New setting syntax", parent=self.setting_rowcolumn3)
		mc.text(label="", parent=self.setting_rowcolumn3)
		mc.text(label="", parent=self.setting_rowcolumn3)

		self.setting_syntax_textfield = mc.textField(parent=self.setting_rowcolumn3)
		mc.button(label="Save syntax", parent=self.setting_rowcolumn3, command=self.save_new_syntax_function)
		mc.button(label="Reset default", parent=self.setting_rowcolumn3, command=self.reset_default_syntax_function)





		self.settings_texture_frame = mc.frameLayout(label="Texture settings", parent=self.settings_main_scroll, width=self.window_width, collapsable=True, collapse=False)
		"""
		number of list to print in this settings page
			- shading render engine menu

			FOR EACH TEXTURE CHANNEL
			- texture channel
				- texture keyword list
				- input node + output
				- final node + input
		"""
		self.render_engine_menu = mc.optionMenu(label="Render Engine", parent=self.settings_texture_frame)
		for render_engine in self.shader_settings_dictionnary:
			mc.menuItem(parent=self.render_engine_menu,label=str(render_engine))



		mc.separator(style="none", height=10, parent=self.settings_texture_frame)
		self.settings_channel_editor_frame = mc.frameLayout(label="Channel Editor", parent=self.settings_texture_frame, width=self.window_width, collapsable=True, collapse=True)
		"""
		CREATE CHANNEL
			informations needed:
				name of the channel
		DELETE CHANNEL
			selection in the channel box
		"""
		self.channel_editor_rowcolumnlayout = mc.rowColumnLayout(numberOfColumns=2, parent=self.settings_channel_editor_frame, columnWidth=((1, self.window_width/2), (2, self.window_width/2)))
		mc.text(label="Name of the channel to create", parent=self.channel_editor_rowcolumnlayout)
		mc.text(label="", parent=self.channel_editor_rowcolumnlayout)
		self.new_channel_textfield = mc.textField(parent=self.channel_editor_rowcolumnlayout)
		mc.button(label="Create channel", parent=self.channel_editor_rowcolumnlayout, command=self.create_new_channel_function)

		mc.button(label="Delete channel", parent=self.settings_channel_editor_frame, command=self.delete_existing_channel_function)

		self.settings_keyword_editor_frame = mc.frameLayout(label="Keyword Editor", parent=self.settings_texture_frame, width=self.window_width, collapsable=True, collapse=True)
		mc.text(label="Keyword list", parent=self.settings_keyword_editor_frame)
		self.keyword_list_textfield = mc.textField(parent=self.settings_keyword_editor_frame)
		mc.button(label="Save keywords", parent=self.settings_keyword_editor_frame, command=self.save_texture_keyword_function)




		self.shading_settings_rowcolumn1 = mc.rowColumnLayout(numberOfColumns=2, parent=self.settings_texture_frame, columnWidth=((1, self.window_width/4), (2, int(self.window_width - self.window_width/4))))

		mc.text(label="Channel List", parent=self.shading_settings_rowcolumn1)
		mc.text(label="", parent=self.shading_settings_rowcolumn1)

		self.channel_textscrolllist = mc.textScrollList(height=self.window_height,allowMultiSelection=False,parent=self.shading_settings_rowcolumn1, selectCommand=partial(self.refresh_shading_settings_list_function, "channel"))

		#self.shading_settings_column = mc.columnLayout(adjustableColumn=True)
		self.shading_settings_right_column = mc.columnLayout(adjustableColumn=True, parent=self.shading_settings_rowcolumn1)
		self.shading_settings_rowcolumn2 = mc.rowColumnLayout(numberOfColumns=3, parent=self.shading_settings_right_column, columnWidth=((1, self.window_width/4), (2, self.window_width/4), (3, self.window_width/4)))
		
		mc.text(label="Origin node Name", parent=self.shading_settings_rowcolumn2)
		mc.text(label="Origin file Attribute", parent=self.shading_settings_rowcolumn2)
		mc.text(label="Origin node Output", parent=self.shading_settings_rowcolumn2)
		self.origin_node_name_textscrolllist = mc.textScrollList(parent=self.shading_settings_rowcolumn2, selectCommand=partial(self.refresh_shading_settings_list_function, "node_name"))
		self.origin_node_attribute_textscrolllist = mc.textScrollList(parent=self.shading_settings_rowcolumn2)
		self.origin_node_output_textscrolllist = mc.textScrollList(parent=self.shading_settings_rowcolumn2)

		mc.button(label="Save Origin", parent=self.shading_settings_right_column, command=partial(self.change_shading_dictionnary_function, "origin"))
		

		self.shading_settings_rowcolumn3 = mc.rowColumnLayout(numberOfColumns=3, parent=self.shading_settings_right_column, columnWidth=((1, self.window_width/4), (2, self.window_width/4), (3, self.window_width/4)))

		mc.text(label="Middle node Name", parent=self.shading_settings_rowcolumn3)
		mc.text(label="Middle node Input", parent=self.shading_settings_rowcolumn3)
		mc.text(label="Middle node Output", parent=self.shading_settings_rowcolumn3)
		self.middle_node_name_textscrolllist = mc.textScrollList(parent=self.shading_settings_rowcolumn3, selectCommand=partial(self.refresh_shading_settings_list_function, "middle_node_name"))
		self.middle_node_input_textscrolllist = mc.textScrollList(parent=self.shading_settings_rowcolumn3)
		self.middle_node_output_textscrolllist = mc.textScrollList(parent=self.shading_settings_rowcolumn3)

		mc.button(label="Save Middle", parent=self.shading_settings_right_column, command=partial(self.change_shading_dictionnary_function, "middle"))


	
		self.shading_settings_rowcolumn4 = mc.rowColumnLayout(numberOfColumns=2, parent=self.shading_settings_right_column, columnWidth=((1, int((self.window_width-self.window_width/4)/2)), (2, int((self.window_width-self.window_width/4)/2))))
		mc.text(label="Final node Name", parent=self.shading_settings_rowcolumn4)
		mc.text(label="Final node Name input", parent=self.shading_settings_rowcolumn4)
		self.final_node_name_textscrolllist = mc.textScrollList(parent=self.shading_settings_rowcolumn4, selectCommand=partial(self.refresh_shading_settings_list_function, "final_node_name"))
		self.final_node_input_textscrolllist = mc.textScrollList(parent=self.shading_settings_rowcolumn4)

		mc.button(label="Save Final", parent=self.shading_settings_right_column, command=partial(self.change_shading_dictionnary_function, "final"))


		

		#TEXTURES PACKAGE
		if self.project_path != "None":
			#get the render engine
			current_render_engine = mc.optionMenu(self.render_engine_menu, query=True, value=True)
			channel_list = []
			for render_engine, content in self.shader_settings_dictionnary.items():
				if render_engine == current_render_engine:
					for channel in content:
						channel_list.append(channel)
					#append to the list
					mc.textScrollList(self.texture_channel_list, edit=True, append=channel_list)

		self.load_shading_settings_function()












		self.log_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs, height=self.window_height)
		self.log_scroll = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.log_column, height=self.window_height, resizeCommand=self.resize_command_function)

		self.log_program_frame = mc.frameLayout(label="Program Log", labelAlign="top", width=self.window_width, collapsable=True, collapse=True,parent=self.log_scroll)
		self.log_list = mc.textScrollList(parent=self.log_program_frame, allowMultiSelection=False, enable=True, height=self.window_height/2, append=self.log_list_content)

		self.log_team_frame = mc.frameLayout(label="Team logs", width=self.window_width, collapsable=True, collapse=True, parent=self.log_scroll)
		self.lost_team_list = mc.textScrollList(parent=self.log_team_frame, allowMultiSelection=False, enable=True, height=self.window_height/2)


		mc.tabLayout(self.tabs, edit=True, tabLabel=((self.prod_column, "PROD ASSETS"), (self.export_column, "EXPORT"), (self.settings_column, "SETTINGS"), (self.log_column, "LOGS")))






		
		#create and launch the message thread
		
		if self.launch_message_thread != True:
			self.message_thread = threading.Thread(target=self.main_message_thread_function)
			self.message_thread.start()

	


	





	def add_content_in_textfield_function(self):
		selection = mc.textScrollList(self.setting_syntax_list, query=True, si=True)[0]
		mc.textField(self.setting_syntax_textfield, edit=True, text=selection)


	def delete_settings_interface_item_function(self):
		for key in self.settings:
			#DELETE GRAPHIC INTERFACE
			self.button_name = "%s_button"%key
			
			try:
				mc.deleteUI(globals()[self.button_name], control=True)
			except:
				pass

	
	def create_settings_interface_item_function(self):
		name_list = []
		syntax_list = []
		keyword_list = []
		folder_list = []

		for key, value in self.settings.items():
			

			name_list.append(key)
			syntax_list.append(value[0])
			keyword_list.append(value[1])

			if value[2] == None:
				folder_list.append("None")
			else:
				folder_list.append(value[2])

		mc.textScrollList(self.setting_type_list, edit=True, removeAll=True, append=name_list)
		mc.textScrollList(self.setting_syntax_list, edit=True, removeAll=True, append=syntax_list)
		mc.textScrollList(self.setting_keyword_list, edit=True, removeAll=True, append=keyword_list)
		mc.textScrollList(self.settings_folder_list, edit=True, removeAll=True, append=folder_list)


	

		

	def export_name_checkbox_function(self, event):
		checkbox_value = mc.checkBox(self.export_name_checkbox, query=True, value=True)
		
		if checkbox_value == True:
			mc.textField(self.export_name_textfield, edit=True, enable=False)
		else:
			mc.textField(self.export_name_textfield, edit=True, enable=True)

	

		


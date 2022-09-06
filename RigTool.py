"""
RIG TOOL

tools include in the program
	saver / importer curves
	create controller : (from locator selection)
		fk controller
		ik controller
		twist controller
	builder instances attributes
	assign attributes
	controller hierarchy / color settings
"""
import maya.cmds as mc
import pymel.core as pm 
import os
import pickle
import pprint

from functools import partial



#add project path to system path list
def onMayaDroppedPythonFile(*args):
	#create the path for all the functions
	path = '/'.join(__file__.replace("", "/").split("/")[:-1])
	sys.path.append(path)
	print("PATH ADDED TO MAYA")




class Application:	
	def __init__(self):
		letter = "abcdefghijklmnopqrstuvwxyz"
		figure = "0123456789"

		self.list_letter = list(letter)
		self.list_figure = list(figure)
		self.list_capital = list(figure.upper())


		self.curve_list, self.hierarchy_preset = self.load_controller_data_function()
		self.name_list = []
		for element in self.curve_list:
			self.name_list.append(element["short_name"])


		self.window_width = 310


		self.main_interface()






	def main_interface(self):
		#creation of the main interface
		#load all the settings
		self.window = mc.window(sizeable=False)
		mc.columnLayout(adjustableColumn=True)


		#SAVER CURVE TOOL
		self.save_curve_frame = mc.frameLayout(label="Curve Saver Tool", labelAlign="top", width=self.window_width, collapsable=True, collapse=False, backgroundColor=(0.192, 0.352, 0.350), parent=self.window)
		self.save_curve_main_column = mc.rowColumnLayout(numberOfColumns=2, parent=self.save_curve_frame, columnWidth=[(1, self.window_width/2), (2, self.window_width/2)])
		self.save_curve_left_column = mc.columnLayout(adjustableColumn=True, parent=self.save_curve_main_column)
		self.save_curve_right_column = mc.columnLayout(adjustableColumn=True, parent=self.save_curve_main_column)
		#LEFT COLUMN
		mc.text(label="Saved Items", parent=self.save_curve_left_column)
		self.save_tool_saved_items_scrolllist = mc.textScrollList(allowMultiSelection=False, height=250, numberOfRows=15, enable=True, width=self.window_width/2, append=self.name_list, parent=self.save_curve_left_column)
		#RIGHT COLUMN
		mc.text(label="Curve to save Name", parent=self.save_curve_right_column)
		self.curve_name_entry = mc.textField(parent=self.save_curve_right_column)
		mc.button(label="Save Item", command=self.save_curve_function, parent=self.save_curve_right_column)
		mc.button(label="Delete Item", command=self.delete_curve_function, parent=self.save_curve_right_column)
		mc.button(label="Import Item", command=partial(self.import_curve_function, "manual"), parent=self.save_curve_right_column)


		#CONTROLLER RIG TOOL 
		self.rig_tool_frame = mc.frameLayout(label="Rig Tool", labelAlign="top", width=self.window_width, collapsable=True, collapse=False, backgroundColor=(0.192, 0.352, 0.350), parent=self.window)
		#creation of the column inside of the frame
		self.rig_tool_main_column = mc.rowColumnLayout(numberOfColumns=2, parent=self.rig_tool_frame, columnWidth=[(1, self.window_width/2), (2, self.window_width/2)])
		self.rig_tool_left_column = mc.columnLayout(adjustableColumn=True, parent=self.rig_tool_main_column)
		self.rig_tool_right_column = mc.columnLayout(adjustableColumn=True, parent=self.rig_tool_main_column)
		#left column
		#SETTINGS PANEL
		self.settings_rig_tool_frame = mc.frameLayout(label="Settings", labelAlign="top", width=self.window_width/2, collapsable=True, collapse=False, backgroundColor=(0.192, 0.352, 0.350), parent=self.rig_tool_left_column)
		#HIERARCHY EDITOR PANEL 
		self.hierarchy_rig_tool_frame = mc.frameLayout(label="Hierarchy Preset", labelAlign="top", width=self.window_width/2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.rig_tool_left_column)
		#CONTROLLER TOOL
		self.controller_rig_tool_frame = mc.frameLayout(label="Controller Creation", labelAlign="top", width=self.window_width/2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.rig_tool_right_column)
		#AUTO RIG
		self.autorig_rig_tool_frame = mc.frameLayout(label="Auto Rig", labelAlign="top", width=self.window_width/2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.rig_tool_right_column)
		#ATTRIBUTE CREATOR
		self.attribute_rig_tool_frame = mc.frameLayout(label="Attribute Creator", labelAlign="top", width=self.window_width/2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.rig_tool_right_column)

		mc.showWindow()









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

	def save_curve_function(self, event):	
			"""
			function that get the informations of the curve to copy it
			"""
			selected_curves = mc.filterExpand(sm=9)
			if selected_curves == None:
				mc.error("You have to select at least one curve!")
				return


			#get curve informations
			#store them in a dictionary of curve with a name to describe them
			print(selected_curves)
			for curve in selected_curves:
				print(curve)
				curve_info_node = mc.createNode("curveInfo")
				curve_shape_node = mc.listRelatives(curve, shapes=True)[0]
				mc.connectAttr("%s.worldSpace"%curve_shape_node, "%s.inputCurve"%curve_info_node)

				knots = cmds.getAttr( f"curveInfo1.knots[*]" )
				knots = [ int(x) for x in knots ]
				spans = cmds.getAttr( f"{curve}.spans" )
				periodic = bool( cmds.getAttr( f"{curve}.form" ) )
				degree = cmds.getAttr( f"{curve}.degree" )
				cvs = spans + degree
				pts = []
				for i in range( spans ):
				    pts.append( tuple( cmds.xform( f"{curve}.cv[{i}]", q=True, translation=True ) ) )
				max_nb_knots = cvs+degree-1
				nb_knots = len( knots )

				new_pts = pts[:]
				pprint.pprint( new_pts )
				# inv_pts = pts[:0:-1]
				if periodic:
				    for i in range( degree ):
				        new_pts.append( new_pts[i] )

			

				try:
					mc.delete(curve_info_node)
					print("%s deleted"%curve_info_node)
				except:
					break


				
				letter_status = self.letter_verification_function(mc.textField(self.curve_name_entry, query=True, text=True))
				if letter_status == True:
					short_name = mc.textField(self.curve_name_entry, query=True, text=True)
				else:
					short_name = curve
				#check if the dictionnary file exist
				curve_dict = {
							"short_name": short_name,
							"long_name": curve,
							"shape": curve_shape_node,
							"knots": knots,
							"spans":spans,
							"periodic":periodic,
							"degree":degree,
							"cvs":cvs,
							"pts":pts,
							"new_pts":new_pts
						}
				
				try:

					with open("Data/ControllerData.dll", "rb") as read_info:
						curve_list = pickle.load(read_info)
						hierarchy_data = pickle.load(read_info)
					curve_list.append(curve_dict)

				except:
					#recreate an empty dictionnary
					self.curve_list = [
						curve_dict
						]
				#save the new dictionnary
				self.curve_list.append(curve_dict)
				self.save_controller_data_function(self.curve_list, self.hierarchy_preset)

				name_list = []
				for element in self.curve_list:
					name_list.append(element["short_name"])

				print("save on GUI!")
				mc.textScrollList(self.save_tool_saved_items_scrolllist, edit=True, removeAll=True, append=name_list)
				
				"""
				pprint.pprint( new_pts )
				# inv_pts = pts[:0:-1]
				if periodic:
				    for i in range( degree ):
				        new_pts.append( new_pts[i] )

				try:
					instructions = f"mc.curve( point={new_pts}, periodic={periodic}, degree={degree}, knot={knots} )"
					mc.delete(curve_info_node)
					eval( instructions )
				except:
					mc.error("Your curve has to be closed!")"""

	def delete_curve_function(self, event):
		selection = mc.textScrollList(self.save_tool_saved_items_scrolllist, query=True, si=True)
		if selection == None:
			mc.error("You have to select at least one curve to import!")
			return
		else:
			curve_list, self.hierarchy_preset = self.load_controller_data_function()
			if curve_list == False:
				mc.error("Unable to read the curve file!")
				return
			else:
				for element in curve_list:
					print(element)
				for element in selection:

					for i in range(0, len(curve_list)):
						if curve_list[i]["short_name"] == element:
							curve_list.pop(i)
							break
				print("\n")


				self.save_controller_data_function(curve_list, self.hierarchy_preset)

				name_list = []

				for element in curve_list:
					name_list.append(element["short_name"])
				mc.textScrollList(self.save_tool_saved_items_scrolllist, edit=True, removeAll=True, append=name_list)

	def create_controller_manager_data_function(self):
		"""
		create two list
		"""
		self.curve_list = []
		self.preset_rig = 	[
				["transform", "transform", "curve", "joint"],
				["root", "cstr", "c", "sk"]
			]
		
		self.save_controller_data_function(self.curve_list, self.preset_rig)
		return self.curve_list, self.preset_rig

	def save_controller_data_function(self, curve_data, hierarchy_data):
		if os.path.isdir("Data") == False:
			os.mkdir("Data")
		with open("Data/ControllerData.dll", "wb") as save_file:
			pickle.dump(curve_data, save_file)
			pickle.dump(hierarchy_data, save_file)

	def load_controller_data_function(self):
		try:
			with open("data/ControllerData.dll", "rb") as read_file:
				self.curve_list = pickle.load(read_file)
				self.hierarchy_preset = pickle.load(read_file)
		except:
			self.curve_list, self.hierarchy_preset = self.create_controller_manager_data_function()
		return self.curve_list, self.hierarchy_preset

	def import_curve_function(self, mode, event):
		#check the selection in the textscrolllist
		if mode == "manual":
			#selection in textscrolllist
			selection = mc.textScrollList(self.save_tool_saved_items_scrolllist, query=True, si=True)
		else:
			#ctrl_fk_curve variable
			selection = [self.ctrl_fk_curve]

		print(selection)

		if (selection == None) or (len(selection) == 0):
			mc.error("You have to define a curve to import!")
			return
		else:
			#check if the data curve file exist and try to take it content
			curve_list, hierarchy_preset = self.load_controller_data_function()
			if curve_list == False:
				mc.error("Unable to read the curve file!")
				return
			else:
				#go through the list and take the dictionnary of the curve
				for element in selection:
					for curve in curve_list:
						print(element, curve)
						if curve["short_name"]==element:
							curve_dict = curve 
							self.created_curve = mc.curve(point=curve_dict['new_pts'], periodic=curve_dict['periodic'], degree=curve_dict['degree'], knot=curve_dict['knots'])
							mc.warning("Curve created : ", self.created_curve)
							return self.created_curve



Application()
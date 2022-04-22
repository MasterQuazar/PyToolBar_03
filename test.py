import maya.cmds as mc
import pymel.core as pm
import os
import pickle
import pprint

from functools import partial



"""
controller creation tool
	creation of a main hierarchy and main group for the rig

	creation of fk controllers (from joints selection)
	creation of twist controller (from n number of controller between each fk controller + 1 for each fk controller)
	creation of surfaces 
		creation of joints on surfaces	
	creation of ik handle + ik controller

	creation of an instanced attribute controller (for one controller hierarchy)
		creation of attribute for this attribute controller
			switch ik/fk
			auto stretch
			auto hide

	mirror joints button
"""




class Application:
	def __init__(self):

		"""
		try to find the content of the rig hierarchy file data
		if the file doesn't exist create it
		"""
		#letter verification function variables
		letter = "abcdefghijklmnopqrstuvwxyz"
		figure = "0123456789"

		self.list_letter = list(letter)
		self.list_capital = list(letter.upper())
		self.list_figure = list(figure)

		self.attribute_builder = []
		self.attribute_target = []
		self.attribute_list = [
			"visibility"
			]
		"""
		tool to:
			-> create controller
			-> import saved curves
			-> color controller
		"""
		self.window_width = 410
		#curve saver tool variables

			
		self.curve_list, self.hierarchy_preset = self.load_controller_data_function()
		print(self.curve_list)
		self.name_list = []
		for element in self.curve_list:
			self.name_list.append(element["short_name"])

		self.preset_node_list = self.hierarchy_preset[0]
		self.preset_name_list = self.hierarchy_preset[1]
		self.preset_message_list = []

		self.ctrl_fk_curve = None

		for i in range(0, len(self.preset_node_list)):
			self.preset_message_list.append("%s - %s" % (self.preset_node_list[i], self.preset_name_list[i]))

		self.main_interface()





	






	def main_interface(self):
		self.window = mc.window(sizeable=False)
		mc.columnLayout(adjustableColumn=True)

		self.create_controller_frame = mc.frameLayout(label="Controller Tool", labelAlign="top",width=self.window_width, collapsable=True, collapse=False, backgroundColor=(0.192, 0.352, 0.350), parent=self.window)

		#SAVE IMPORT CURVES
		self.create_controller_row_columns = mc.rowColumnLayout(numberOfColumns=2, columnWidth = [(1, self.window_width/2), (2, self.window_width/2)], parent=self.create_controller_frame)
		self.create_controller_left_column = mc.columnLayout(adjustableColumn=True, parent=self.create_controller_row_columns)
		self.create_controller_right_column = mc.columnLayout(adjustableColumn=True, parent=self.create_controller_row_columns)

		#LEFT COLUMN SAVE CURVES
		#3 panel inside
		# curve mode
		# light mode
		mc.text(label="Saved Items", parent=self.create_controller_left_column)
		self.save_tool_saved_items_scrolllist = mc.textScrollList(allowMultiSelection=False, height=250, numberOfRows=15, enable=True, width=self.window_width/2, append=self.name_list, parent=self.create_controller_left_column)

		mc.separator(style="none", height=23, parent=self.create_controller_left_column)
		mc.text(label="Curve to save Name", parent=self.create_controller_left_column)
		self.curve_name_entry = mc.textField(parent=self.create_controller_left_column)
		mc.button(label="Save Item", command=self.save_curve_function, parent=self.create_controller_left_column)
		mc.button(label="Delete Item", command=self.delete_curve_function, parent=self.create_controller_left_column)
		mc.button(label="Import Item", command=self.import_curve_function, parent=self.create_controller_left_column)

		#RIGHT COLUMN CREATE CONTROLLERS
		"""
		Create controller tool
			-> create a locator
			-> or select a locator
			-> validation button to create the controller since you have 
				a locator selected
			-> import saved curve checkbox (take the seleciton in textscrolllist)
			-> can select several locators
		"""
		"""
		edit right preset 
			list of presets in the hierarchy (by order)
			textfield left menu on right
			delete button
			add button
		"""
		mc.text(label="Controller hierarchy preset", parent=self.create_controller_right_column)

		self.hierarchy_preset_ui = mc.textScrollList(numberOfRows=8, allowMultiSelection=True, append=self.preset_message_list ,parent=self.create_controller_right_column)

		self.hierarchy_preset_creation_columns = mc.rowColumnLayout(numberOfColumns=2, columnWidth = [(1, self.window_width/4), (2, self.window_width/4)], parent=self.create_controller_right_column)
		self.hierarchy_preset_left_column=mc.columnLayout(adjustableColumn=True, parent=self.hierarchy_preset_creation_columns)
		self.hierarchy_preset_right_column = mc.columnLayout(adjustableColumn=True, parent=self.hierarchy_preset_creation_columns)
		mc.text(label="Node name", parent=self.hierarchy_preset_left_column)
		self.preset_name_textfield = mc.textField(parent=self.hierarchy_preset_left_column)
		mc.text(label="Node type", parent=self.hierarchy_preset_right_column)
		self.preset_type_menu = mc.optionMenu(parent=self.hierarchy_preset_right_column)
		mc.menuItem(label="transform")
		mc.menuItem(label="joint")
		mc.menuItem(label="curve")
		mc.menuItem(label="locator")
		mc.separator(style="none", height=10)


		self.hierarchy_button_ui = mc.rowLayout(nc=4, adj=4, parent=self.create_controller_right_column)
		mc.button("Create", parent=self.hierarchy_button_ui, command=partial(self.edit_hierarchy_preset_function, "create"))
		mc.button("Delete", parent=self.hierarchy_button_ui, command=partial(self.edit_hierarchy_preset_function, "delete"))
		mc.button("Insert",parent=self.hierarchy_button_ui, command=partial(self.edit_hierarchy_preset_function, "insert"))
		mc.button("Rename",parent=self.hierarchy_button_ui, command=partial(self.edit_hierarchy_preset_function, "rename"))


		mc.separator(style="singleDash", height=20, parent=self.create_controller_right_column)
		mc.separator(style="none", parent=self.create_controller_right_column, height=5)
		mc.button(label="Define controller curve by default", parent=self.create_controller_right_column, command=self.define_controller_by_default_function)
		mc.separator(style="none", parent=self.create_controller_right_column, height=5)


		self.spline_controller_frame = mc.frameLayout(label="SplineNeckHips Auto Rig", labelAlign="top", width=self.window_width/2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.create_controller_right_column)
		mc.text(label="Spline Controller Color", parent=self.spline_controller_frame)
		self.spline_controller_fk_color_ui = mc.colorIndexSliderGrp(min=1, max=31, value=1, parent=self.spline_controller_frame)
		#create an ik hierarchy
		self.spline_controller_ik_checkbox = mc.checkBox(label="Ik hierarchy", value=True, changeCommand=self.enable_spline_controller_ik_color_function)
		self.spline_controller_ik_color_ui = mc.colorIndexSliderGrp(min=1, max=31, value=1, parent=self.spline_controller_frame, enable=True)
		mc.button(label="Create Spline and Neck Rig", command=self.create_spline_function, parent=self.spline_controller_frame)
		self.spline_instanced_attribute_color_ui = mc.colorIndexSliderGrp(min=1, max=31, value=1, parent=self.spline_controller_frame)
		mc.button(label="Create builder instanced attributes", command=partial(self.build_instanced_attributes_function, "attributes_spline"))



		self.attribute_frame = mc.frameLayout(label="Attribute Creator", labelAlign="top", width=self.window_width / 2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.create_controller_right_column)
		mc.text(label="Attributes list", parent=self.attribute_frame)
		self.attribute_list_ui = mc.textScrollList(numberOfRows=15, parent=self.attribute_frame, allowMultiSelection=True, append=self.attribute_list)
		#button to define the item that will receive the attribute
		#button to define targets of the attribute
		self.attribute_name_ui = mc.textField(parent=self.attribute_frame)
		mc.button(label="Define the builder attribute", command=self.define_attribute_builder, parent=self.attribute_frame)
		mc.button(label="Define targets of the attributes", command=self.define_attribute_target, parent=self.attribute_frame)
		mc.button(label="CREATE ATTRIBUTE", command=self.apply_attribute_function, parent=self.attribute_frame)


		mc.separator(style="singleDash", height=15, parent=self.create_controller_frame)
		mc.button(label="CREATE HOOK", parent=self.create_controller_frame, command=self.create_hook_function)
		mc.separator(style="none", height=15, parent=self.create_controller_frame)














		mc.showWindow()








	def define_attribute_builder(self, event):
		selection = mc.ls(sl=True, sn=True)
		self.attribute_builder = selection 
	def define_attribute_target(self, event):
		selection = mc.ls(sl=True, sn=True)
		self.attribute_target = selection 

	def apply_attribute_function(self, event):
		#get the selection of items and targets
		if (self.attribute_builder == None) or (self.attribute_target==None):
			mc.error("You have to define builders and target!")
			return
		#get the content of the attribute selection
		attr_selection = mc.textScrollList(self.attribute_list_ui, query=True, si=True)
		#get the content of the textfield
		attr_name = mc.textField(self.attribute_name_ui, query=True, text=True)


		for builder in self.attribute_builder:
			for attr in attr_selection:
				if attr == "visibility":
					#check the len of target elements
					if len(self.attribute_target) != 1:
						mc.error("You have to select only one target!")
					#creation of the attribute
					mc.addAttr((mc.listRelatives(builder, children=True))[0], longName="visibility_%s" % self.attribute_target[0], attributeType="bool", keyable=True)
					#creation of the fac attribute
					new_attr = "visibility_%s"%self.attribute_target[0]
					float_constant = mc.createNode("floatConstant", n="facAttr_for_%s_%s" % (attr, self.attribute_target[0]))
					print("%s.%s" % (mc.listRelatives(builder, children=True)[0], new_attr))
					print("%s.inFloat"%(float_constant))
					mc.connectAttr( "%s.%s" % (mc.listRelatives(builder, children=True)[0], new_attr), "%s.inFloat" % (float_constant) )
					mc.connectAttr("%s.outFloat"%(float_constant), "%s.visibility"%(self.attribute_target[0]))



	def color_curve_function(self, curve, color):
		mc.setAttr("%s.overrideEnabled"%curve, 1)
		mc.setAttr("%s.overrideColor"%curve, color)

	def build_instanced_attributes_function(self, attribute_name, event):
		#select a curve in the saved curve tool
		try:
			self.ctrl_fk_curve = mc.textScrollList(self.save_tool_saved_items_scrolllist, query=True, si=True)[0]
		except:
			pass
		if self.ctrl_fk_curve == None:
			mc.error("You have to select a curve!")
			return
		else:
			#import the curve and create a locator
			created_curve = self.import_curve_function("spline_attribute_creation")
			self.ctrk_fk_curve = None
			#put this curve in the first transform of the preset hierarchy
			h_node_list = self.hierarchy_preset[0]
			h_name_list = self.hierarchy_preset[1]

			
			for i in range(0, len(h_node_list)):
				if h_node_list[i] == "transform":
					root = mc.createNode("transform", n="%s_%s"% (h_name_list[i], attribute_name))
					mc.parent(created_curve, root)
					break
			for i in range(0, len(h_node_list)):
				if h_node_list[i] == "curve":
					try:
						created_curve = mc.rename(created_curve, "%s_%s" % (h_name_list[i], attribute_name))
						self.color_curve_function(created_curve, int(mc.colorIndexSliderGrp(self.spline_instanced_attribute_color_ui, query=True, value=True))-1)
						mc.scale(6, 6, 6, created_curve, componentSpace=True, scaleXY=True)
						break
					except:
						pass

			#create a locator
			#locator_t = mc.createNode("locator", n="builder_instanced_%s" % (attribute_name))
			locator_s = mc.createNode("locator")
			locator_t = mc.listRelatives(locator_s, parent=True)
			locator_s = mc.rename(locator_s, "builder_instanced_%s_shape"%attribute_name)
			locator_t = mc.rename(locator_t, "builder_instanced_%s"%attribute_name)

			#hide all the attributes of the locator transform
			for attr in mc.listAttr(locator_s, channelBox=True, visible=True):
				mc.setAttr("%s.%s"%(locator_s, attr), keyable=False, channelBox=False)

			#create a separation attribute on the locator
			mc.addAttr(locator_s, longName="separator1", niceName="---|%s|---"%attribute_name.replace("attributes_", ""), attributeType="enum", keyable=True, hidden=False, enumName="-------------")
			mc.warning("Spline created!")
			
					
	def create_hook_function(self, event):
		#get the selection
		selection = mc.ls(sl=True, sn=True)
		#check the len of selection
		#if len % 2 != 0 -> fail
		if (selection == None) or (len(selection)%2 != 0):
			mc.error("You have to select a pair number of things!")
			return
		hooker_list = []
		hooked_list = []
		"""
		for 2 elements
		x -> hooker (transmit matrices)
		y -> hooked (receive matrices)

		Un -> n % 2 = 0 (pair number)
		U0 hook U1
		U...
		Un hook Un+1
		"""
		for i in range(0, len(selection)):
			if i % 2 == 0:
				hooker_list.append(selection[i])
			else:
				hooked_list.append(selection[i])
		for i in range(0, len(hooker_list)):
			#create a transform
			#parent this transform to parents of the hooked item
			#parent all hooked item's children to this transform
			#connect hooker's worldmatrix to hooked offset matrix
			parent = mc.listRelatives(hooked_list[i], parent=True)
			hook_transform = mc.createNode("transform", n="hook_%s_for_%s"%(hooker_list[i], hooked_list[i])) 
			mc.parent(hooked_list[i], hook_transform)
			mc.connectAttr('%s.worldMatrix'%hooker_list[i], "%s.offsetParentMatrix"%hook_transform)
		
	def enable_spline_controller_ik_color_function(self, event):
		value = mc.checkBox(self.spline_controller_ik_checkbox, query=True, value=True)
		mc.colorIndexSliderGrp(self.spline_controller_ik_color_ui, edit=True, enable=value)

	def define_controller_by_default_function(self, event):
		#get selection in textscrolllist of saved curves
		try:
			selection = mc.textScrollList(self.save_tool_saved_items_scrolllist, query=True, si=True)[0]
		except:
			mc.error("You have to select a saved curve!")
			return
		else:
			self.ctrl_fk_curve = selection
			mc.warning("Controller curve defined successfully!")
			return

	"""
	get the locator selection
	get the ctrl name
	"""
	def create_spline_function(self, event):
		ik_controller = []
		ik_root = []

		#check locator selection
		locator_selection = [obj for obj in cmds.ls(sl=True) if cmds.listRelatives(obj, shapes=True, type="locator")]
		if (locator_selection == None) or (len(locator_selection)==0):
			mc.error("You have to select locators")
		#call the function to create controllers
		if mc.checkBox(self.spline_controller_ik_checkbox, query=True, value=True)==True:
			fk_controller, fk_root = self.create_controller_function(locator_selection, "spline_fk_ik")
		else:
			fk_controller, fk_root = self.create_controller_function(locator_selection, "spline_fk")
		#modification of the color and the translation of the created controllers
		#get the selected color
		ctrl_fk_color = mc.colorIndexSliderGrp(self.spline_controller_fk_color_ui, query=True, value=True)
		ctrl_ik_color = mc.colorIndexSliderGrp(self.spline_controller_ik_color_ui, query=True, value=True)
		
		if self.ctrl_fk_curve == None:
			mc.error("You have to select a curve!")
			return
		#creation of the ik hierarchy
		#get checkbox value
		if mc.checkBox(self.spline_controller_ik_checkbox, query=True, value=True) == True:
			#call the function
			ik_controller, ik_root = self.create_controller_function(locator_selection, "spline_ik")
			
			if len(fk_controller) != len(ik_root):
				mc.error("Can't parent ik to fk hierarchy!")
				return
			else:
				for i in range(0, len(fk_controller)):
					mc.parent(ik_root[i], fk_controller[i])

		created_controller = fk_controller + ik_controller 

		for controller in created_controller:
			mc.xform(controller, t=[0, 0, 0])
		for controller in fk_controller:
			self.color_curve_function(controller, int(ctrl_fk_color)-1)
		mc.scale(6, 6, 6, fk_controller[0], componentSpace=True, scaleXY=True)

		#creation of target transforms!!!
		target1=mc.createNode("transform", n="target")
		target2=mc.createNode("transform", n="target")

		if mc.checkBox(self.spline_controller_ik_checkbox, query=True, value=True)==True:
			mc.parent(target1, ik_controller[0])
			mc.parent(target2, ik_controller[-1])

			for controller in ik_controller:
				self.color_curve_function(controller, int(ctrl_ik_color) - 1 )
				mc.scale(1.2, 1.2, 1.2, controller, componentSpace=True, scaleXY=True)
		else:
			mc.parent(target1, fk_controller[0])
			mc.parent(target2, fk_controller[-1])
		mc.warning("SPLINE HIERARCHY CREATED SUCCESSFFULLY!")
		return

	def create_controller_function(self, item, command):
		#get the list for the hierarchy preset
		h_name_list = self.hierarchy_preset[1]
		h_node_list = self.hierarchy_preset[0]
		h_parent = None 
		created_curve = None
		created_controller = []
		root_list = []
		x = 0
		for obj in item:
			#get the name of the controller
			if (command == "spline_fk") or (command == "spline_fk_ik"):
				ctrl_name = "fk_" + obj.replace("loc_", "")
			if (command == "spline_ik"):
				ctrl_name = "ik_" + obj.replace("loc_", "")

			for i in range(0, len(h_name_list)):
				#create each item of the hierarchy
				#creation of a curve
				if x != 0:
					if h_name_list[i] == h_name_list[0]:
						if created_curve != None:
							h_parent = created_curve

				if h_node_list[i] == "curve":
					created_curve = self.import_curve_function("controller_creation")
					if created_curve == None:
						mc.error("Failed to create the controller curve!")
						return
					mc.parent(created_curve, h_parent)
					created_curve = mc.rename(created_curve, "%s_%s" % (h_name_list[i], ctrl_name))
					created_controller.append(created_curve)
					h_parent = "%s_%s" % (h_name_list[i], ctrl_name)
				else:
					#creation of an other node
					if h_name_list[i] == h_name_list[0]:
						#create a root list
						root_list.append("%s_%s"%(h_name_list[i], ctrl_name))
					if (h_node_list[i] == "joint") and (command == "spline_fk_ik"):
						pass
					else:
						new_node = mc.createNode(h_node_list[i], n = "%s_%s" % (h_name_list[i], ctrl_name), p=h_parent)
					h_parent=new_node

				
			x += 1	
		for i in range(0, len(root_list)):
			#match transform all root with the locator that match
			mc.matchTransform(root_list[i], item[i])
		if (command == "spline_fk") or (command == "spline_ik") or (command == "spline_fk_ik"):	
			#creation of the target for the hips and the shoulders at the end of their hierarchy
			"""
			FK HIERARCHY 
				parent the target transform (hips / shoulders) to the first / last controller's curve (FK CONTROLLER)
			IK / FK HIERARCHY
				parent the target transform (hips / shoulders) to the first / last controller's curve (IK CONTROLLER)

			create a setting button to define to which elements thoses target transform should be hooked!
			"""

			return created_controller, root_list

	#TEXTSCROLLLIST EDIT FUNCTIONS
	def edit_hierarchy_preset_function(self, command, event):
		#check the selection in textscrolllist
		selection = mc.textScrollList(self.hierarchy_preset_ui, query=True, si=True)

		if (command != "create") and (selection != None):
			for element in selection:
				item = element.split(" - ")
				if command == "delete":
					for i in range(0, len(self.preset_name_list)):
						if item[1] == self.preset_name_list[i]:
							if item[0] == self.preset_node_list[i]:
								self.preset_name_list.pop(i)
								self.preset_node_list.pop(i)
								break

				if command == "insert":
					#check the rank of the selection
					for i in range(0, len(self.preset_name_list)):
						if (item[1] == self.preset_name_list[i]) and (item[0] == self.preset_node_list[i]):
							#check the content of field
							new_node_name = mc.textField(self.preset_name_textfield, query=True, text=True)
							new_node_type = mc.optionMenu(self.preset_type_menu, query=True, value=True)
							if (self.letter_verification_function(new_node_name))==False:
								mc.error("You have to define a name")
								return
							else:
								#check if the name is already taken
								if (new_node_name == item[1]) and (new_node_type == item[0]):
									mc.error("This name is already taken!")
									return
								else:
									self.preset_name_list.insert(i, new_node_name)
									self.preset_node_list.insert(i, new_node_type)
									break

				if command == "rename":
					#get content of field and menu
					new_node_name = mc.textField(self.preset_name_textfield, query=True, text=True)
					new_node_type = mc.optionMenu(self.preset_type_menu, query=True, value=True)
					if self.letter_verification_function(new_node_name)==False:
						mc.error("You have to rename this item with an other name!")
						return
					for i in range(0, len(self.preset_name_list)):
						if (new_node_name == self.preset_name_list[i]) and (new_node_type == self.preset_node_list[i]):
							mc.error("This name is already taken!")
							return
					for i in range(0, len(self.preset_name_list)):
						if (self.preset_name_list[i] == item[1]) and (self.preset_node_list[i] == item[0]):
							#rename
							self.preset_name_list[i] = new_node_name 
							self.preset_node_list[i] = new_node_type

			

					

				self.save_controller_data_function(self.curve_list, [self.preset_node_list, self.preset_name_list])
				self.preset_message_list = []
				for i in range(0, len(self.preset_node_list)):
					self.preset_message_list.append("%s - %s" % (self.preset_node_list[i], self.preset_name_list[i]))
				mc.textScrollList(self.hierarchy_preset_ui, edit=True, removeAll=True, append=self.preset_message_list)
				
				
		elif command == "create":
			#get content in text field and menu
			new_node_name = mc.textField(self.preset_name_textfield, query=True, text=True)
			new_node_type = mc.optionMenu(self.preset_type_menu, query=True, value=True)

			if (self.letter_verification_function(new_node_name)) == False:
				mc.error("You have to define a name!")
				return
			else:
				for i in range(0, len(self.preset_name_list)):
					if new_node_name == self.preset_name_list[i]:
						if new_node_type == self.preset_node_list[i]:
							mc.error("This name is already taken for the same node!")
							return

				#create a new item in the list
				self.preset_node_list.append(new_node_type)
				self.preset_name_list.append(new_node_name)

				dictionnary = [
					self.preset_node_list,
					self.preset_name_list
					]
				self.save_controller_data_function(self.curve_list, dictionnary)

				#update content of the textscrolllist
				self.preset_message_list = []
				for i in range(0, len(self.preset_node_list)):
					self.preset_message_list.append("%s - %s" % (self.preset_node_list[i], self.preset_name_list[i]))
				mc.textScrollList(self.hierarchy_preset_ui, edit=True, removeAll=True, append=self.preset_message_list)
		else:
			mc.error("You have to select something in the list!")
			return








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

			for curve in selected_curves:
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

			

				for i in iter(int, 1):
					try:
						mc.delete("curveInfo%s"%i)
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

	def import_curve_function(self, event):
		#check the selection in the textscrolllist
		selection = mc.textScrollList(self.save_tool_saved_items_scrolllist, query=True, si=True)
		if (selection == None) and (event != "controller_creation") and (event != "spline_attribute_creation"):
			mc.error("You have to select at least one curve to import!")
			return
		else:
			if (event == "controller_creation") or (event == "spline_attribute_creation"):
				selection = [self.ctrl_fk_curve]

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
							return self.created_curve
							


Application()
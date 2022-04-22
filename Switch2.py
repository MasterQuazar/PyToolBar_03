import maya.cmds as mc
import os
import sys
import pickle
import pymel.core as pm

from functools import partial





class Application:
	def __init__(self):
		letter = "abcdefghijklmnopqrstuvwxyz"
		figure = "0123456789"

		self.list_letter = list(letter)
		self.list_capital = list(letter.upper())
		self.list_figure = list(figure)
		"""
		PROGRAM THAT ALLOW YOU TO CREATE CONTROLLER PRESET
		"""
		self.window_width = 310

		self.shape_controller_list = []
		self.joints_list = []
		self.controller_list = []
		self.switch_controller = None
		self.ik_controller = None
		self.keyframe_delta = 1

		self.animation_preset = self.load_animation_preset_function()
		self.animation_preset_name_list = []

		for element in self.animation_preset:
			self.animation_preset_name_list.append(element["name"])
		self.main_interface()




	def main_interface(self):
		"""
		create a preset of selection
			-> name of the preset
			-> name of the fk controller
			-> linked jnts
			-> ik switch controller with its switch attribute
		FROM IK TO FK
			-> jnts coordonates (rotation) into fk controller
		FROM FK TO IK
			-> fk controller coordinates into jnts coordonates
		"""
		self.window = mc.window(sizeable=False)
		


		self.animation_switch_frame = mc.frameLayout(label="Frame Range Focus Tool", collapsable=True, collapse=False, width=self.window_width, backgroundColor=(0.635, 0.134, 0.074))
		self.animation_switch_main_column=mc.columnLayout(adjustableColumn=True, parent=self.animation_switch_frame)

		#panel to create animation switch preset
		#name of the preset -> controller -> joint
		mc.text(label="Animation switch preset list", parent=self.animation_switch_main_column)
		self.animation_preset_ui = mc.textScrollList(allowMultiSelection=True, numberOfRows=8, parent=self.animation_switch_main_column, append=self.animation_preset_name_list)

		mc.separator(style="none", height=10, parent=self.animation_switch_main_column)

		self.animation_switch_rowcolumn=mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, self.window_width/2), (2, self.window_width/2)])
		self.animation_switch_left_column= mc.columnLayout(adjustableColumn=True, parent=self.animation_switch_rowcolumn)
		self.animation_switch_right_column=mc.columnLayout(adjustableColumn=True, parent=self.animation_switch_rowcolumn)
		mc.text(label="Name of the preset", parent=self.animation_switch_left_column)
		self.animation_preset_textfield = mc.textField(parent=self.animation_switch_left_column)
		mc.text(label="Name of the switch attribute")
		self.animation_preset_switch_ui = mc.textScrollList(parent=self.animation_switch_right_column, numberOfRows=8, allowMultiSelection=False)

		mc.button("Define switch controller", parent=self.animation_switch_right_column, command=self.define_switch_ctrl_function)
		mc.button("Define Controllers", parent=self.animation_switch_left_column, command=self.define_controllers_function)
		mc.button("Define Joints", parent=self.animation_switch_left_column, command=self.define_joints_function)
		mc.button("Define IK Handle", parent=self.animation_switch_left_column, command=self.define_ik_handle_function)

		mc.separator(style="none", height=35, parent=self.animation_switch_left_column)

		mc.button(label="Load attributes", parent=self.animation_switch_left_column, command=self.load_switch_attribute_function)

		


		mc.separator(style="none", height=15, parent=self.animation_switch_main_column)

		mc.button("CREATE SWITCH PRESET", parent=self.animation_switch_main_column, command=self.create_switch_preset_function)
		mc.button("REMOVE SWITCH PRESET", parent=self.animation_switch_main_column, command=self.delete_switch_preset_function)
		mc.button("CHANGE SWITCH PRESET", parent=self.animation_switch_main_column)

		mc.separator(style="singleDash", height=25, parent=self.animation_switch_main_column)
		self.animation_switch_keyframe_row = mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, self.window_width/2), (2, self.window_width/2)], parent=self.animation_switch_main_column)
		mc.text(label="Keyframe delta", parent=self.animation_switch_keyframe_row)
		self.keyframe_delta_ui = mc.intField(value = 1, minValue=1)
		mc.button("SWITCH IK FK", parent=self.animation_switch_main_column, command=self.switch_ik_fk_function)
		

		

		mc.showWindow()




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



	def load_switch_attribute_function(self, event):
		selection = mc.ls(sl=True)
		selection_shape = mc.listRelatives(mc.ls(sl=True), parent=True)
		if selection == None:
			mc.error("You have to select something!")
			return
		if len(selection) != 1:
			mc.error("You have to select only one thing!")
			return

		selection_attr = mc.listAttr(selection, visible=True, keyable=True)
		selection_shape_attr = mc.listAttr(selection_shape, visible=True, keyable=True)

		attr_list = []

		for element in selection_attr:
			attr_list.append("TRANSFORM-%s"%element)
		for element in selection_shape_attr:
			attr_list.append("SHAPE-%s"%element)
		mc.textScrollList(self.animation_preset_switch_ui, edit=True, removeAll=True, append=attr_list)



	def load_animation_preset_function(self):
		#check the workspace
		self.project = mc.workspace(query=True, rd=True)
		info = []

		if os.path.isfile(os.path.join(self.project, "scripts/SwitchPreset.dll"))==False:
			return self.create_animation_preset_function(info)
		else:
			try:
				with open(os.path.join(self.project, "scripts/SwitchPreset.dll"), "rb") as read_file:
					return pickle.load(read_file)
			except:
				
				return self.create_animation_preset_function(info)



	def create_animation_preset_function(self, animation_preset):
		#create a new file of empty presets
		with open(os.path.join(self.project, "scripts/SwitchPreset.dll"), "wb") as save_file:
			pickle.dump(animation_preset, save_file)
		return animation_preset 



	def define_joints_function(self, event):
		joint_selection = mc.ls(sl=True, type="joint")
		if joint_selection == None:
			mc.error("You have to select at least one joint!")
			return
		else:
			self.joints_list = joint_selection
			for element in self.joints_list:
				print(element)
			mc.warning("Joints defined successfully!")


	def define_controllers_function(self, event):
		shape_controller_selection = mc.listRelatives(mc.ls(sl=True), type="nurbsCurve")
		transform_controller_selection = mc.listRelatives(shape_controller_selection, parent=True)
		


		#control that the len of the three_list isn't empty!!
		if (shape_controller_selection == None) or (transform_controller_selection == None):
			mc.error("You have to select at least one controller!")
			return
		else:

			
			#save the list of all the controllers and joints
			self.controller_list = transform_controller_selection
			self.shape_controller_list = shape_controller_selection

			for element in self.controller_list:
				print(element)
			mc.warning("Controllers defined successfully!")




	def define_switch_ctrl_function(self, event):
		#get the selection and list all its attributes
		selection = mc.ls(sl=True)
		shape_selection = mc.listRelatives(selection, parent=True)
		textscroll_selection = mc.textScrollList(self.animation_preset_switch_ui, query=True, si=True)

		#check if selection is empty
		if selection == None:
			mc.error("You have to select something!")
			return
		if textscroll_selection == None:
			mc.error("You have to select an attribute!")
			return
		if len(selection) != 1:
			mc.error("You must select only one thing!")
			return
		textscroll_selection = textscroll_selection[0].split("-")
		if textscroll_selection[0] == "TRANSFORM":
			self.switch_controller = (selection[0], textscroll_selection[1])
		else:
			self.switch_controller = (selection[0], textscroll_selection[1])
		mc.warning("Switch controller defined successfully!")
		return
		


	def create_switch_preset_function(self, event):
		#get all informations
		if len(self.joints_list) == 0:
			mc.error("You have to select joints!")
			return
		elif len(self.controller_list) == 0:
			mc.error("You have to select controllers!")
			return
		elif len(self.controller_list) != len(self.joints_list):
			mc.error("You have to select as many joints as controllers!")
		elif self.switch_controller == None:
			mc.error("You have to select a switch controller!")
			return
		elif self.ik_controller == None:
			mc.error("You have to select an ik controller!")
			return
		else:
			preset_name = mc.textField(self.animation_preset_textfield, query=True, text=True)
			if self.letter_verification_function(preset_name)==False:
				mc.error("You have to select a name for the switch preset!")
				return
			if (preset_name in self.animation_preset_name_list)==True:
				mc.error("You already have a preset with this name!")
				return

			#get min and max values of the switch attribute
			min_value = mc.attributeQuery(self.switch_controller[1], n=self.switch_controller[0], min=True)[0]
			max_value = mc.attributeQuery(self.switch_controller[1], n=self.switch_controller[0], max=True)[0]

			#create the dictionnary of informations
			#we will append the dictionnary to the list of presets
			preset_info = {
				"name": preset_name,
				"limits":[min_value, max_value],
				"switch": self.switch_controller,
				"ik_controller": self.ik_controller,
				"controllers": self.controller_list,
				"joints": self.joints_list
			}
			#try to save the new dictionnary in the file
			self.animation_preset.append(preset_info)

			self.animation_preset_name_list.append(preset_info["name"])
			#save the new list of preset
			self.create_animation_preset_function(self.animation_preset)
			mc.textScrollList(self.animation_preset_ui, edit=True, removeAll=True, append=self.animation_preset_name_list)
			mc.warning("IK / FK PRESET CREATED AND SAVED SUCCESSFULLY!")

			self.switch_controller = None
			self.controller_list = []
			self.joints_list = []
			self.ik_controller = None
			return



	def delete_switch_preset_function(self, event):
		#get the selection in the textscrolllist
		preset_selection = mc.textScrollList(self.animation_preset_ui, query=True, si=True)
		if preset_selection == None:
			mc.error("You have to select a preset to delete!")
			return
		else:
			for element in preset_selection:
				for i in range(0, len(self.animation_preset)):
					if self.animation_preset[i]["name"] == element:
						self.animation_preset.pop(i)
						break
			for element in self.animation_preset_name_list:
				self.animation_preset_name_list.remove(element)
			#save the new preset list
			self.create_animation_preset_function(self.animation_preset)
			mc.textScrollList(self.animation_preset_ui, edit=True, removeAll=True, append=self.animation_preset_name_list)
			mc.warning("IK / FK PRESET REMOVED SUCCESSFULLY!")



	def define_ik_handle_function(self, event):
		controller_selection = mc.ls(sl=True)

		if controller_selection == None:
			mc.error("You have to select a controller!")
			return
		if len(controller_selection) != 1:
			mc.error("You have to select only one controller!")
			return
		self.ik_controller = controller_selection[0]

		mc.warning("Ik handle defined successfully!")
		return




	def switch_ik_fk_function(self, event):
		#get all informations from dictionnary
		#check the selection in textscrolllist
		switch_preset = mc.textScrollList(self.animation_preset_ui, query=True, si=True)
		delta = mc.intField(self.keyframe_delta_ui, query=True, value=True)

		if switch_preset == None:
			mc.error("You have to select at least one preset to switch!")
			return
		else:
			for element in switch_preset:
				for i in range(0, len(self.animation_preset)):
					if self.animation_preset[i]["name"] == element:
						info = self.animation_preset[i]
						break

				mc.setKeyframe()
				ik_controller = info["ik_controller"]
				controllers = info["controllers"]
				joints = info["joints"]
				switch_ctrl = info["switch"][0]
				switch_attr = info["switch"][1]
				#detect the max value of the attribute
				min_value = info["limits"][0]
				max_value = info["limits"][1]

				


				if mc.getAttr("%s.%s"%(switch_ctrl, switch_attr)) == min_value:
					mc.setKeyframe(switch_ctrl, at=switch_attr, value=int(max_value), t=(int(mc.currentTime(query=True)) + delta))
					print("FK TO IK")

					#coordinates of the last controller (worldspace)
					#go in the ik handle coordinates (worldspace)
					rotation = mc.xform(controllers[-1], query=True, ro=True, worldSpace=True)
					translation = mc.xform(controllers[-1], query=True, t=True, worldSpace=True)

					mc.xform(ik_controller, ro=rotation, t=translation, worldSpace=True)
					print(rotation)
					print(translation)


				if mc.getAttr("%s.%s"%(switch_ctrl, switch_attr)) == max_value:
					mc.setKeyframe(switch_ctrl, at=switch_attr, value=int(min_value), t=(int(mc.currentTime(query=True)) + delta))
					print("IK TO FK")
					#take the coordinates of all the joints rotate (worldspace)
					#and put them into controllers rotate (worldspace)
					#print all link between joints and controllers (in order)
					for i in range(0, len(controllers)):
						rotation = mc.xform(joints[i], query=True, ro=True, worldSpace=True)
						mc.xform(controllers[i], ro=rotation, worldSpace=True)

				mc.setKeyframe()


					
						
					



Application()
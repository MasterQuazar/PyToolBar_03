import maya.cmds as mc
import sys
import os
import maya.OpenMaya as OpenMaya
import pymel.core as pm 
import numpy as np
import maya.mel as mel 
import pickle

from random import randrange
from random import uniform
from functools import partial
from pymel import core





class AnimApplication:

		


	def build_anim_interface_function(self):
		print("AnimInterface built")
		self.pack_function_list["Anim"] = ["EaseAnimTool", "AnimationSwitchTool"]


		##############################################################################################################################################################################################
		#ANIM PANEL
		##############################################################################################################################################################################################

		#EASE IN EASE OUT TOOL
		self.EaseAnimTool=mc.frameLayout(visible=False, label="EaseIn / EaseOut Tool", collapsable=True, collapse=True, width=self.window_width, backgroundColor=(0.635, 0.134, 0.074), parent=self.main_column)
		mc.separator(style="none", height=5)
		mc.button(label="Save Keys", command=self.save_ini_keys, parent=self.EaseAnimTool)
		self.slider_delta1_value = mc.floatSlider(min=-20, max=20, value=0, step=0.1, changeCommand=self.get_values_function, width=self.window_width/4, parent=self.EaseAnimTool)
		self.slider_delta2_value = mc.floatSlider(min=-20, max=20, value=0, step=0.1, changeCommand=self.get_values_function, width=self.window_width/4, parent=self.EaseAnimTool)
		mc.button(label="Reset Keys", command=self.reset_ini_keys, parent=self.EaseAnimTool)





		#SWITCH IK FK SCRIPT
		self.AnimationSwitchTool = mc.frameLayout(visible=False, label="Switch IK / FK Tool", collapsable=True, collapse=True, width=self.window_width, backgroundColor=(0.635, 0.134, 0.074), parent=self.main_column)

		#panel to create animation switch preset
		#name of the preset -> controller -> joint
		mc.text(label="Animation switch preset list", parent=self.AnimationSwitchTool)
		self.animation_preset_ui = mc.textScrollList(allowMultiSelection=True, numberOfRows=8, parent=self.AnimationSwitchTool, append=self.animation_preset_name_list)

		mc.separator(style="none", height=10, parent=self.AnimationSwitchTool)

		self.animation_switch_rowcolumn=mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, self.window_width/2), (2, self.window_width/2)], parent=self.AnimationSwitchTool)
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

		


		mc.separator(style="none", height=15, parent=self.AnimationSwitchTool)

		mc.button("CREATE SWITCH PRESET", parent=self.AnimationSwitchTool, command=self.create_switch_preset_function)
		mc.button("REMOVE SWITCH PRESET", parent=self.AnimationSwitchTool, command=self.delete_switch_preset_function)
		mc.button("CHANGE SWITCH PRESET", parent=self.AnimationSwitchTool)

		mc.separator(style="singleDash", height=25, parent=self.AnimationSwitchTool)
		self.animation_switch_keyframe_row = mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, self.window_width/2), (2, self.window_width/2)], parent=self.AnimationSwitchTool)
		mc.text(label="Keyframe delta", parent=self.animation_switch_keyframe_row)
		self.keyframe_delta_ui = mc.intField(value = 1, minValue=1, parent=self.animation_switch_keyframe_row)
		mc.button("SWITCH IK FK", parent=self.AnimationSwitchTool, command=self.switch_ik_fk_function)








	def save_ini_keys(self, event):
		objects=pm.ls(sl=1)
		self.item_selection = pm.selectionConnection('graphEditor1FromOutliner', q=1, object=1)

		if len(self.item_selection) != 1:
			mc.error("You have to select only one curve")
			return
		self.ini_x= mc.keyframe(query=True, sl=True)
		self.ini_y = []

		for item in self.ini_x:
			self.ini_y.append(mc.getAttr(self.item_selection[0], t=item))





	def reset_ini_keys(self, event):
		if len(self.ini_x)!=0:
			for i in range(0, len(self.ini_x)):
				print(self.item_selection, self.ini_x[i], self.ini_y[i])
				mc.setKeyframe(self.item_selection, v=self.ini_y[i], time=self.ini_x[i])
		else:
			return








	def get_values_function(self, event):
		"""
		get item selection and his attribute
		get the keytime values
		get the keyattr values
		"""

		objects=pm.ls(sl=1)
		self.item_selection = pm.selectionConnection('graphEditor1FromOutliner', q=1, object=1)

		if len(self.item_selection) != 1:
			mc.error("You have to select only one curve")
			return
		x = mc.keyframe(query=True, sl=True)
		y = []

		if x == None:
			mc.error("You have to select keys")
			return

		for item in x:
			y.append(mc.getAttr(self.item_selection[0], t=item))

		P0, P3 = np.array([x[0], y[0]]), np.array([x[-1], y[-1]])

		def OtherPs(P0, dt0, P3, dt3):
		    if dt0 <= 0:
		        P1 = (P0[0], P0[1] + dt0) if P0[1] > P3[1] else (P0[0], P0[1] - dt0)
		    else:
		        P1 = (P0[0] + dt0, P0[1])
		    if dt3 <= 0:
		        P2 = (P3[0] + dt3, P3[1])
		    else:
		        P2 = (P3[0], P3[1] - dt3) if P3[1] > P0[1] else (P3[0], P3[1] + dt3)
		    return np.array(P1), np.array(P2)

		DELTA_0 = (mc.floatSlider(self.slider_delta1_value, query=True, value=True))# INTENSITE DE LA PENTE AU POINT P0, varie entre [-inf, +inf]
		DELTA_3 = (mc.floatSlider(self.slider_delta2_value, query=True, value=True))# INTENSITE DE LA PENTE AU POINT P3, varie entre [-inf, +inf]

		P1, P2 = OtherPs(P0, DELTA_0, P3, DELTA_3)

		cubicB = lambda t: (1-t)**3*P0 + 3*(1-t)**2*t*P1 + 3*(1-t)*t**2*P2 + t**3*P3
		bez = [cubicB(i) for i in np.linspace(0, 1, 1000)]
		new_y = [min(bez, key=lambda t: np.abs(t[0] - j))[1] for j in x]

		for i in range(1, len(x)-1):
		    mc.setKeyframe(self.item_selection, v=new_y[i], time=x[i])





	def delete_anim_range_function(self, event):
		project = mc.workspace(q=True, rd=True)
		#check the selection of the anim range list
		selection = mc.textScrollList(self.anim_range_list_ui, query=True, si=True)[0].split(" ")[0]
		if selection == None:
			mc.error("You have to select an anim range to delete!")
			return
		else:
			
			try:
				with open(os.path.join(project, "scripts/AnimRangeData.dll"), "rb") as read_file:
					anim_range_dict = pickle.load(read_file)
			except:
				mc.error("Impossible to load AnimRangeData.dll")
				return
			else:
				for i in range(0, len(anim_range_dict)):
					if anim_range_dict[i]["name"] == selection:
						del anim_range_dict[i]
						break
				"""
				except:
					mc.warning("Impossible to delete the frame range set!")
				else:"""
				with open(os.path.join(project, "scripts/AnimRangeData.dll"), "wb") as save_file:
					pickle.dump(anim_range_dict, save_file)
				print("Anim frame range successfully deleted!")

				frame_range_name_list = []
				for element in anim_range_dict:
					frame_range_name_list.append("%s [%s ; %s]" % (element["name"], element["min"], element["max"]))
				mc.textScrollList(self.anim_range_list_ui, edit=True, removeAll=True, append=frame_range_name_list)


	def save_anim_range_function(self, event):
		project = mc.workspace(q=True,rd=True)
		#control the content of each fields
		#	letters for the name
		#	min value and max values?
		"""
			-> max value > min value
			-> content in the name of the anim frame range
		"""
		frame_range_name = mc.textField(self.frame_range_name_ui, query=True, text=True)
		letter_status = self.letter_verification_function(frame_range_name)
		if letter_status == False:
			mc.error("You have to define a name for this frame range!")
			return
		min_frame = mc.intField(self.min_frame_ui, query=True, value=True)
		max_frame = mc.intField(self.max_frame_ui, query=True, value=True)
		if max_frame <= min_frame:
			mc.error("The end frame has to be strictly superior than the start one!")
			return
		frame_range_dict = {
			"name":frame_range_name,
			"min":min_frame,
			"max":max_frame
		}
		self.anim_range_list.append(frame_range_dict)

		frame_range_name_list = []
		for element in self.anim_range_list:
			frame_range_name_list.append("%s [%s ; %s]" % (element["name"], element["min"], element["max"]))

		#try to save the new_list in the project folder
		if os.path.isdir(os.path.join(project, "scripts"))==False:
			os.mkdir(os.path.join(project, "scripts"))

		try:
			with open(os.path.join(project,"scripts/AnimRangeData.dll"), "wb") as save_file:
				pickle.dump(self.anim_range_list, save_file)
		except:
			mc.error("Impossible to save AnimRange in your project")
			return
		else:
			mc.textScrollList(self.anim_range_list_ui, edit=True, removeAll=True, append=frame_range_name_list)
			mc.warning("AnimRange saved successfully!")



	def set_anim_range_function(self, event):
		selection = mc.textScrollList(self.anim_range_list_ui,query=True, si=True)[0].split(" ")[0]
		print(selection)

		if selection != None:
			for element in self.anim_range_list:
				if element["name"]==selection:
					#set start and end frames
					mc.playbackOptions(minTime=element["min"], maxTime=element["max"])
		else:
			mc.error("You have to select one frame range!")
			return




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





					
						
			
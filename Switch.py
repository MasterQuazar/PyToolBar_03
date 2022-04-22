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
		self.animation_switch_textfield = mc.textField(parent=self.animation_switch_right_column)

		mc.button("Define switch controller", parent=self.animation_switch_right_column, command=self.define_switch_ctrl_function)
		mc.button("Define joints and controller", parent=self.animation_switch_left_column, command=self.define_jnts_ctrl_function)
		mc.button("Define IK Handle", parent=self.animation_switch_right_column, command=self.define_ik_handle_function)

		


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





	def define_jnts_ctrl_function(self, event):
		#get the selection of jnts and curves
		selection = mc.filterExpand(sm=9)
		controller_selection = mc.listRelatives(selection, parent=True, fullPath=False)
		joint_selection = []

		real_selection = mc.ls(sl=True)
		print(real_selection)


		for element in real_selection:
			if pm.objectType(element) == "joint":
				joint_selection.append(element.replace("Shape", ""))

		print(real_selection)
		print(controller_selection)
		print(joint_selection)
		if (len(joint_selection)==0) or (controller_selection==None):
			mc.error("You have to select at least one controller and one joint!")
			return
		else:
			self.joints_list = joint_selection
			self.controller_list = controller_selection
			mc.warning("Joints / Controllers defined successfully!")
			print("hello world!")



	def define_switch_ctrl_function(self, event):
		#get the content of the switch ctrls name textfield
		#if its empty return an error
		#controller selection
		switch_ctrl_name = mc.ls(sl=True)

		"""
		for i in range(0, len(switch_ctrl_name)):
			switch_ctrl_name[i] = switch_ctrl_name[i].replace("Shape", "")"""
			
		switch_attr_name = mc.textField(self.animation_switch_textfield, query=True, text=True)

		if self.letter_verification_function(switch_attr_name)==False:
			mc.error("You have to choose with attribute of the controller define a switch ik/fk")
			return
		#list all attributes of the controller and try to find the switch attribute (textfield)
		sn_attr = mc.listAttr(sn=True)
		ln_attr = mc.listAttr(sn=False)
		for element in sn_attr:
			if element == switch_attr_name:
				
				self.switch_controller = [switch_ctrl_name[0], switch_attr_name]
				print(self.switch_controller)
				mc.warning("Switch controller defined successfully!")
				return
		mc.error("This attribute doesn't exist on this controller!")
		return




	def create_switch_preset_function(self, event):
		#get all informations
		if len(self.joints_list) == 0:
			mc.error("You have to select joints!")
			return
		elif len(self.controller_list) == 0:
			mc.error("You have to select controllers!")
			return
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
		#check that the selection if a controller
		ik_handle = mc.ls(sl=True,sn=True)
		if (ik_handle != None) and (len(ik_handle) == 1):
			self.ik_controller = ik_handle 
			mc.warning("Ik controller defined successfully!")
			return
		else:
			mc.error("You have to select only one controller!")
			return



	def switch_ik_fk_function(self, event):
		#get the value of the keyframe delta
		delta = mc.intField(self.keyframe_delta_ui, query=True, value=True)
		"""
		get the selection of the textscrolllist
		load all the informations
		check the status of the ik attribute
			ik -> fk
			fk -> ik
		ik to fk
			-> all joints in all controllers
		fk to ik
			-> all controlers in jnts
		"""
		preset_selection = mc.textScrollList(self.animation_preset_ui, query=True, si=True)

		if preset_selection != None:
			for preset in preset_selection:
				#load the dictionnary
				for key in self.animation_preset:
					if key["name"] == preset:
						preset_dictionnary = key
						break
				#detect the value of the attribute
				#if 0 -> FK
				#if 1 -> IK
				ik_fk_value = mc.getAttr("%s.%s" % (preset_dictionnary["switch"][0], preset_dictionnary["switch"][1]))
				
				#put a setkeyframe of the current attribute at the current time
				#put the switch 2 frames after
				if ik_fk_value == preset_dictionnary["limits"][1]:
					#SWITCH TO FK		
					#take coordinates of all joints
					#put them into controllers
					#change the value of the ikfk attr
					mc.setKeyframe(preset_dictionnary["switch"][0], at=preset_dictionnary["switch"][1], value=int(preset_dictionnary["limits"][0]), t=(int(mc.currentTime(query=True)) + delta))

					for i in range(0, len(preset_dictionnary["joints"])):
						attr_list = mc.listAttr(preset_dictionnary["controllers"][i], visible=True, keyable=True)
		
					
						#translate = mc.xform(preset_dictionnary["joints"][i], query=True, t=True, worldSpace=True)
						rotate = mc.xform(preset_dictionnary["joints"][i], query=True, ro=True, worldSpace=False)

						#mc.xform(preset_dictionnary["controllers"][i], t=translate, worldSpace=True)
						mc.xform(preset_dictionnary["controllers"][i], ro=rotate, worldSpace=False)

						print(preset_dictionnary["joints"][i], " -> ", preset_dictionnary["controllers"][i])


				if ik_fk_value == preset_dictionnary["limits"][0]:
					#SWITCH TO IK
					#take the coordinates of the ik last controller of the hierarchy
					#put those coordinates in the ik handle coordinates!
					last_controller = preset_dictionnary["controllers"][-1]
					ik_controller = preset_dictionnary["ik_controller"]

					#set the keyframe on the ik controller
					#set the keyrfame on the ik switch
					mc.setKeyframe(preset_dictionnary["switch"][0], at=preset_dictionnary["switch"][1], value=int(preset_dictionnary["limits"][1]), t=(int(mc.currentTime(query=True)) + delta))

					translate = mc.xform(last_controller, query=True, t=True, worldSpace=True)
					rotate = mc.xform(last_controller, query=True, ro = True, worldSpace=True)

					mc.xform(ik_controller, t=translate, worldSpace=True)
					mc.xform(ik_controller, ro=rotate, worldSpace=True)

				mc.setKeyframe()





					
						
					




		else:
			mc.error("You have to select a preset!")
			return



Application()
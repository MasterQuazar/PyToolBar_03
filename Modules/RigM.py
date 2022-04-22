import maya.cmds as mc
import sys
import os
import pprint
import pickle
import maya.OpenMaya as OpenMaya
import pymel.core as pm 
import numpy as np
import maya.mel as mel 

from random import randrange
from random import uniform
from functools import partial
from pymel import core





class RigApplication:
	def build_rig_interface_function(self):
		print("RigInterface built")
		self.pack_function_list["Rig"] = ["RenameTool", "HookTool", "CenterTool", "ConnexionTool"]

		##############################################################################################################################################################################################
		#RIG PANEL
		##############################################################################################################################################################################################	

		#RENAMETOOL
		self.RenameTool = mc.frameLayout(visible=False, label="Rename Tool", labelAlign="top",width=self.window_width, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.main_column)
		self.rename_menu = mc.optionMenu(width=(self.window_width/2), changeCommand=self.rename_interface_settings, parent=self.RenameTool)
		mc.menuItem(label="Replace Mode")
		mc.menuItem(label="Prefix Mode")
		mc.menuItem(label="Suffix Mode")
		self.rename_field1 = mc.textField(parent=self.RenameTool)
		self.rename_field2 = mc.textField(parent=self.RenameTool)

		mc.button(label="Rename", command=self.rename_function,parent=self.RenameTool)

		
		#HOOK CREATION TOOL
		self.HookTool = mc.frameLayout(visible=False, label="Hook Tool", labelAlign="top", width=self.window_width, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350),parent=self.main_column)
		mc.separator(style="none", height=5, parent=self.HookTool)
		mc.button("CreateHook", command=self.create_hook_function, parent=self.HookTool)
		
		#CENTER TOOL
		self.CenterTool = mc.frameLayout(visible=False, label="Center Tool", labelAlign="top", width=self.window_width, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.main_column)
		mc.separator(style="none", height=5, parent=self.CenterTool)
		mc.button("FindCenter", command=self.find_center_function, parent=self.CenterTool)
	
		#CONNEXION EDITOR
		self.ConnexionTool = mc.frameLayout(visible=False, label="Connexion Tool", labelAlign="top", width=self.window_width, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.main_column)
		self.connexion_tool_row_column1 = mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, self.window_width/2), (2, self.window_width/2)],parent=self.ConnexionTool)

		#creation of the four list panel
		#2 that take origin and target items
		#2 that take origin and target attr (all attr)
		self.origin_items_panel = mc.textScrollList(numberOfRows=6, enable=False, width=self.window_width/2, parent=self.connexion_tool_row_column1)
		self.target_items_panel = mc.textScrollList(numberOfRows=6, enable=False, width=self.window_width/2, parent=self.connexion_tool_row_column1)
		
		self.connexion_tool_row_column2 = mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, self.window_width/2), (2, self.window_width/2)], parent=self.ConnexionTool)
		self.origin_attr_panel = mc.textScrollList(allowMultiSelection=True,numberOfRows=15, enable=True, width=self.window_width/2, parent=self.connexion_tool_row_column2)
		self.target_attr_panel = mc.textScrollList(allowMultiSelection=True,numberOfRows=15, enable=True, width=self.window_width/2, parent=self.connexion_tool_row_column2)
		mc.button(label="ORIGINS", width=(self.window_width/2), command=partial(self.define_items_function, "origin"), parent=self.connexion_tool_row_column2)
		mc.button(label="TARGETS", width=(self.window_width/2), command=partial(self.define_items_function, "target"), parent=self.connexion_tool_row_column2)
		


		#DEFINE A CONSTANT (mult double linear node connexion)
		self.connexion_constant_field = mc.textField(width=self.window_width, enable=False, parent=self.ConnexionTool)
		self.connexion_constant_checkbox = mc.checkBox(label="Constant", offCommand=self.disable_connexion_field, onCommand=self.enable_connexion_field, parent=self.ConnexionTool)

		#CREATE CONNEXIONS BUTTON
		mc.button(label="CREATE CONNEXIONS", width=self.window_width/2, command=self.connexions_condition_function, parent=self.ConnexionTool)
		









	#RENAME TOOL
	def rename_interface_settings(self, event):
		menu_value = mc.optionMenu(self.rename_menu, query=True, value=True)

		if menu_value == "Replace Mode":
			mc.textField(self.rename_field1, edit=True, enable=True)
			mc.textField(self.rename_field2, edit=True, enable=True)
		else:
			mc.textField(self.rename_field2, edit=True, enable=False)



	def rename_function(self, event):
		menu_value = mc.optionMenu(self.rename_menu, query=True, value=True)

		#textfield content
		textfield1 = mc.textField(self.rename_field1, query=True, text=True)
		textfield2 = mc.textField(self.rename_field2, query=True, text=True)

		#check the len of the selection
		#check if there is something to replace
		selection = mc.ls(sl=True, sn=True)
		if (selection == None):
			mc.error("You have to select something!")
			return
		letter_value = self.letter_verification_function(textfield1)

		if menu_value == "Replace Mode":
			if letter_value == False:
				mc.error("There is nothing to replace!")
				return
			else:
				#replace the old content by the new one for each element in the selection
				for element in selection:
					mc.rename(element, element.replace(textfield1, textfield2))
		else:
			content_to_insert = mc.textField(self.rename_field1, query=True, text=True)

			if menu_value == "Prefix Mode":
				#put the value before the name
				for element in selection:
					mc.rename(element, str(content_to_insert + element))
			if menu_value == "Suffix Mode":
				#put the value after the name
				for element in selection:
					mc.rename(element, str(element + content_to_insert))












	#CREATE HOOK TOOL
	def create_hook_function(self, event):
		"""
		HOOK CREATION ALGORYTHM

		SELECTION
			-> 2 items selected
			-> n % 2 = 0 items selected (1-2; 3-4; ...; n-n+1)
			-> creation of the list (parents, hooked, hooker)

		CREATION OF THE HOOK
			create the transform 
				put it into the hierarchy
				parent the hooked to the transform
			make the connexion between the hooker and the hooked
			lock the attributes of the hook transform
				translate
				rotate
				scale
				shear
				inherits transform
		"""
		#check the selection
		self.selection = mc.ls(sl=True, sn=True)

		if len(self.selection)==0:
			mc.error("SELECTION IS EMPTY")
		if (len(self.selection)%2)!=0:
			mc.error("YOU HAVE TO SELECT 2 ITEMS PER HOOK")
		else:
			list_hooked = []
			list_hooker = []
			list_parent = []

			i=0
			while i < len(self.selection):
				if i%2 == 0:
					list_hooked.append(self.selection[i])
					list_parent.append(mc.listRelatives(self.selection[i], parent=True))
				else:
					list_hooker.append(self.selection[i])
				i+=1
			print(list_hooker)
			print(list_hooked)
			#hook for loop
			list_transform_hook = []
			for hooker in list_hooked:
				for element in list_hooker:
					#create transforms and parents them to hierarchy
					list_transform_hook.append("hook_%s"%hooker)
					mc.createNode("transform",n="hook_%s"%hooker)
					if mc.listRelatives(element, parent=True)!=None:
						mc.parent("hook_%s"%hooker, mc.listRelatives(element, parent=True))
					mc.parent(element, "hook_%s"%hooker)
					#lock attributes
					mc.setAttr("hook_%s"%hooker+".translate", lock=True)
					mc.setAttr("hook_%s"%hooker+".rotate", lock=True)
					mc.setAttr("hook_%s"%hooker+".scale", lock=True)
					mc.setAttr("hook_%s"%hooker+".shear", lock=True)
					mc.setAttr("hook_%s"%hooker+".inheritsTransform", False, lock=True)


			i = 0
			while i < len(list_hooked):
				mc.connectAttr(list_hooked[i]+".worldMatrix", list_transform_hook[i]+".offsetParentMatrix")
				i+=1









	#FIND CENTER TOOL
	def find_center_function(self, event):
		self.selection = mc.ls(sl=True)
		self.coreselection = core.ls(sl=1)[0]
		"""
		check the selection type to get the center
			-mesh
			-edges
			-faces
			-vertex
		different ways to get the center depending of the type
		then get the center of the all things

		create a list by types
		"""
		
		self.vertex_list = mc.filterExpand(self.selection, sm=31)
		self.mesh_list = (mc.ls(sl=True, dag=True, type="mesh"))
		self.edges_list = mc.filterExpand(self.selection, sm=32)


		if self.vertex_list == None:
			self.vertex_list = []
		#creation of the vertices list to define the center
		if self.edges_list != None:
			for element in self.edges_list:
				self.vertex_list.append(mc.polyListComponentConversion(element, tv=True))
			for item in self.vertex_list:
				for vertex in item:
					pos = (mc.pointPosition(vertex, world=True))
					mc.spaceLocator(p=(pos[0],pos[1],pos[2]))

		elif self.vertex_list != None:
			for vertex in self.vertex_list:
				pos = (mc.pointPosition(vertex, world=True))
				mc.spaceLocator(p=(pos[0],pos[1],pos[2]))

		if self.mesh_list != None:
			for element in self.mesh_list:
				pos = (mc.objectCenter(element))
				mc.spaceLocator(p = (pos[0], pos[1], pos[2]))

		#get the list of all the locator
		self.locator_list = mc.ls(type="locator",long=True) or []
		#create the final locator
		self.final_locator = mc.spaceLocator(p=(0,0,0),n="FinalLocator")

		
		#for each element of the list get only the name of the element
		for element in self.locator_list:
			name = (element.split("|"))[1]
			#center pivot for each locator
			mc.xform(name, centerPivots=True)
			#creation of the parentisation of the locators
			mc.parentConstraint(name, self.final_locator[0], maintainOffset=False)
		mc.delete(self.final_locator,constraints=True)
		for element in self.locator_list:
			mc.delete(element)
			name = (element.split("|"))[1]
			mc.delete(name)
			print("%s deleted"%element)









	def disable_connexion_field(self, event):
		mc.textField(self.connexion_constant_field, edit=True, enable=False)
	def enable_connexion_field(self, event):
		mc.textField(self.connexion_constant_field, edit=True, enable=True)



	def define_items_function(self, command, event):
		#get the selection in the outliner
		selection = mc.ls(sl=1, sn=True)
		#check if the selection is empty
		if len(selection)==0:
			mc.error("You have to select something")
			return
		else:
			#define the list of the attributes
			attr_list = []
			for element in selection:
				for attr in mc.listAttr(element):
					if (attr in attr_list)==False:
						attr_list.append(attr)

			#fill the attr and items panels
			if command=="origin":
				self.list_origin_attr = []
				mc.textScrollList(self.origin_items_panel, edit=True, removeAll=True)
				mc.textScrollList(self.origin_items_panel, edit=True, append=selection)

				self.list_origin_attr = attr_list
				self.list_origin_items = [selection][0]
				mc.textScrollList(self.origin_attr_panel, edit=True, removeAll=True)
				mc.textScrollList(self.origin_attr_panel, edit=True, append=attr_list)
				
			if command=="target":
				self.list_target_attr = []
				mc.textScrollList(self.target_items_panel, edit=True, removeAll=True)
				mc.textScrollList(self.target_items_panel, edit=True, append=selection)

				self.list_target_items = [selection][0]
				self.list_target_attr = [attr_list]
				mc.textScrollList(self.target_attr_panel, edit=True, removeAll=True)
				mc.textScrollList(self.target_attr_panel, edit=True, append=attr_list)
			return



	def connexions_condition_function(self, event):
		#get origin / target attr list
		
		self.selected_origin_attr = mc.textScrollList(self.origin_attr_panel, q=1, si=1)
		self.selected_target_attr = mc.textScrollList(self.target_attr_panel, q=1, si=1)
		#connexions creation conditions
		"""
		-> 1 origin and n target
		-> n origin and n target 

		-> 1 attr origin and n attr target
		-> n attr origin and n attr target
		"""
		#check the len of all list (equal 0 ?)
		for target in self.list_target_items:
			if (target in self.list_origin_items)==True:
				mc.error("ConnexionError - an element is used as origin and as target")
				return

		if (len(self.list_origin_items)==0) or (len(self.list_target_items)==0) or (self.selected_origin_attr==None) or (self.selected_target_attr==None) or(len(self.selected_origin_attr)==0) or (len(self.selected_target_attr)==0):
			mc.error("SelectionError - empty list detected")
			return
		else:
			if (len(self.list_origin_items) == 1) or (len(self.list_origin_items) == len(self.list_target_items)):
				if (len(self.selected_origin_attr) == 1) or (len(self.selected_origin_attr) == len(self.selected_target_attr)):
					self.connexions_function()
					return
			mc.error("SelectionError - invalid number of selections")
			return



	def make_connexions_function(self, origin_item, target_item, origin_attr, target_attr):
		print("%s.%s -> %s.%s"% (origin_item, origin_attr, target_item, target_attr))
		try:
			if mc.checkBox(self.connexion_constant_checkbox, query=True, value=True)==False:
				mc.connectAttr(origin_item+"."+origin_attr, target_item+"."+target_attr)
			else:
				constant = int(mc.textField(self.connexion_constant_field, query=True, text=True))
				#create a mult double linear node
				#connect the origin in the input 1 
				#put the constant in the input 2
				double_linear = mc.createNode("multDoubleLinear")
				mc.setAttr(double_linear+".input2", constant)
				mc.connectAttr(origin_item+"."+origin_attr, double_linear+".input1")
				mc.connectAttr(double_linear+".output", target_item+"."+target_attr)
			print("connexion made")

		except:
			mc.error("connexion failed")
		return



	def connexions_function(self):
		#try to connect element in the list*
		"""
		1 - 1;n
			1->0 ; 1->1; 1->...; 1->n
		2 - n;n
			0->0; 1->1; ...; n->n
		"""
		if len(self.list_origin_items)==len(self.list_target_items):
			if len(self.selected_origin_attr)==len(self.selected_target_attr):
				i = 0
				while i < len(self.list_origin_items):
					y = 0
					while y < len(self.selected_origin_attr):
						self.make_connexions_function(self.list_origin_items[i], self.list_target_items[i], self.selected_origin_attr[y], self.selected_target_attr[y])
						y+=1
					i+=1
			if len(self.selected_origin_attr) != len(self.selected_target_attr):
				i = 0
				while i < len(self.list_origin_items):
					for o in self.selected_origin_attr:
						for t in self.selected_target_attr:
							self.make_connexions_function(self.list_origin_items[i], self.list_target_items[i], o, t)
					i+=1

		if len(self.list_origin_items) != len(self.list_target_items):
			if len(self.selected_origin_attr)==len(self.selected_target_attr):
				for origin_item in self.list_origin_items:
					for target_item in self.list_target_items:
						i = 0
						while i < len(self.selected_origin_attr):
							self.make_connexions_function(origin_item, target_item, self.selected_origin_attr[i], self.selected_target_attr[i])
							i+=1
			if len(self.selected_origin_attr)!=len(self.selected_target_attr):
				for origin_item in self.list_origin_items:
					for target_item in self.list_target_items:
						for origin_attr in self.selected_origin_attr:
							for target_attr in self.selected_target_attr:
								self.make_connexions_function(origin_item, target_item, origin_attr, target_attr)











	def set_controller_position(self, event):
		ctrl_name = mc.textField(self.ctrl_entry, query=True, text=True)
		self.loc_creation_ctrl = mc.spaceLocator(absolute=True, name="loc_%s"%(ctrl_name), position=(0,0,0))
		mc.button(self.create_controller_button, e=True, enable=True)




	def create_controller_function(self, event):
		#get the location of the self.locator
		locx = mc.getAttr("%s.translateX"%self.loc_creation_ctrl[0])
		locy = mc.getAttr("%s.translateY"%self.loc_creation_ctrl[0])
		locz = mc.getAttr("%s.translateZ"%self.loc_creation_ctrl[0])
		"""
			controller hierarchy
			ctrls_
				root_m
					cstr_m
						c_m
							sk_
		"""	
		ctrl_name = mc.textField(self.ctrl_entry, query=True, text=True)
		ctrl_type = mc.checkBox(self.ctrl_checkbox, query=True, value=True)
		
		#check the content of the controller name
		print(ctrl_name, self.letter_verification_function(ctrl_name))
		if self.letter_verification_function(ctrl_name)==False:
			return
		else:
			new_curve=mc.circle(nr=(1,0,0), c=(0,0,0), r=1.5, n='c_%s'%ctrl_name)[0]

			#create transform nodes
			root=mc.createNode("transform", n="root_%s"%ctrl_name)
			cstr=mc.createNode("transform", n="cstr_%s"%ctrl_name)
			joint=mc.joint(p=(locx,locy,locz),n="sk_%s"%ctrl_name)


			#color the new curve in yellow (AS ALL THE FUCKING CONTROLLERS)
			#move the curve to the right position (locator position)
		
			mc.delete(new_curve, constructionHistory=True)
			
			

			#parents all the differents items of the controller
			mc.parent(joint,new_curve)
			mc.parent(new_curve, cstr)
			mc.parent(cstr, root)



			element = [root, cstr, joint]

			if ctrl_type == True:
				ctrl=mc.createNode("transform", n="ctrl_%s"%ctrl_name)
				mc.parent(root, ctrl)
				element.append(ctrl)

			#reset all the pivot position and freeze transformations
			for item in element:
				mc.xform(item, piv=(locx, locy, locz))

			mc.setAttr(root+".translateX", locx)
			mc.setAttr(root+".translateY", locy)
			mc.setAttr(root+".translateZ", locz)

			#search for a lot directories, if it don't exist, create it
			#put the locator inside
			node_list = mc.ls()
			loc_grp=False
			for item in node_list:
				if (item=="LOC"):
					if (mc.nodeType(item))=="transform":
						loc_grp=item
						break
			if loc_grp==False:
				mc.createNode("transform", n="LOC")
				loc_grp="LOC"
			mc.parent(self.loc_creation_ctrl[0], loc_grp)










	def selection_settings_function(self, event):
		selection_mode = mc.optionMenu(self.selection_menu, query=True, value=True)

		#select all curves
		if selection_mode == "Name":
			mc.textField(self.controller_to_color, edit=True, enable=True)
		else:
			mc.textField(self.controller_to_color, edit=True, enable=False)
			if selection_mode == "All":
				mc.select(all=True)
				selection = mc.ls(sn=False)
				self.crvs = mc.filterExpand(selection, sm=9)

				if len(self.crvs) !=None:
					for i in range(0, len(self.crvs)):
						if i%2 == 0:
							self.crvs.pop(i)





	def color_function(self, event):
		selection_mode = mc.optionMenu(self.selection_menu, query=True, value=True)
		color_value = mc.colorIndexSliderGrp(self.controller_color, query=True, value=True)

		if selection_mode == "Name":
			controller_name = mc.textField(self.controller_to_color, query=True, text=True)
			try:
				mc.select(controller_name)
				selection = mc.ls(sl=True, sn=False)
			except ValueError:
				mc.error("You have to select a curve that exist")
				return
			else:
				self.crvs = mc.filterExpand(sm=9)
		if selection_mode == "Selection":
				selection = mc.ls(sl=True, sn=False)
				self.crvs = mc.filterExpand(selection, sm=9)
		print(self.crvs, type(self.crvs))
		print(color_value)
		print(type(color_value))
		#loop that color curves 
		try:
			for element in self.crvs:
				mc.setAttr(element+".overrideEnabled", 1)
				mc.setAttr(element+".overrideColor", int(color_value)-1)

		except TypeError:
			mc.error("You have to select a curve")












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
				#create curve info node
				curve_info_node = mc.createNode("curveInfo")
				curve_shape_node = mc.listRelatives(curve, shapes=True)[0]
				mc.connectAttr("%s.worldSpace"%curve_shape_node, "%s.inputCurve"%curve_info_node)

				knots = mc.getAttr( f"curveInfo1.knots[*]" )
				knots = [ int(x) for x in knots ]
				spans = mc.getAttr( f"{curve}.spans" )
				periodic = bool( mc.getAttr( f"{curve}.form" ) )
				degree = mc.getAttr( f"{curve}.degree" )
				cvs = spans + degree
				pts = []
				for i in range( spans ):
				    pts.append( tuple( mc.xform( f"{curve}.cv[{i}]", q=True, translation=True ) ) )
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


				#instructions = f"mc.curve( point={new_pts}, periodic={periodic}, degree={degree}, knot={knots} )"
				#eval( instructions )


				
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
					with open("Data/CurveManagerData.dll", "rb") as read_info:
						curve_list = pickle.load(read_info)
					curve_list.append(curve_dict)

				except:
					#recreate an empty dictionnary
					curve_list = [
						curve_dict
						]
				#save the new dictionnary
				with open("Data/CurveManagerData.dll", "wb") as save_info:
					pickle.dump(curve_list, save_info)

				name_list = []
				for element in curve_list:
					name_list.append(element["short_name"])

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
			curve_list = self.load_curve_file()
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
				for element in curve_list:
					print(element)
				#save the new dictionnary
				with open("Data/CurveManagerData.dll", "wb") as save_file:
					pickle.dump(curve_list, save_file)

				name_list = []
				for element in curve_list:
					name_list.append(element["short_name"])
				mc.textScrollList(self.save_tool_saved_items_scrolllist, edit=True, removeAll=True, append=name_list)




	def load_curve_file(self):
		try:
			with open("data/CurveManagerData.dll", "rb") as read_file:
				return pickle.load(read_file)
		except:
			return False


	def import_curve_function(self, event):
		#check the selection in the textscrolllist
		selection = mc.textScrollList(self.save_tool_saved_items_scrolllist, query=True, si=True)
		if selection == None:
			mc.error("You have to select at least one curve to import!")
			return
		else:
			#check if the data curve file exist and try to take it content
			curve_list = self.load_curve_file()
			if curve_list == False:
				mc.error("Unable to read the curve file!")
				return
			else:
				#go through the list and take the dictionnary of the curve
				for element in selection:
					for curve in curve_list:
						if curve["short_name"]==element:
							curve_dict = curve 
							try:
								instructions = f"mc.curve( point={curve_dict['new_pts']}, periodic={curve_dict['periodic']}, degree={curve_dict['degree']}, knot={curve_dict['knots']} )"
								eval( instructions )
							except:
								mc.error("Importation error!")
								return


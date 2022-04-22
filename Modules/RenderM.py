import maya.cmds as mc
import sys
import os
import maya.OpenMaya as OpenMaya
import pymel.core as pm 
import numpy as np
import maya.mel as mel 

from random import randrange
from random import uniform
from functools import partial
from pymel import core






class RenderApplication:
		

		

	def build_render_interface_function(self):
		print("RenderInterface built")
		self.pack_function_list["Render"] = ["RandomLambertTool", "RandomizeTool", "ReferencedLightsTool"]
		##############################################################################################################################################################################################
		#RENDER PANEL
		##############################################################################################################################################################################################
		"""mc.frameLayout(visible=False, label="Shader Creator Tool", labelAlign="top", width=self.window_width, collapsable=True, collapse=True, backgroundColor=(0.138, 0.102, 0.224))
		mc.text(label="New shader name")
		self.shader_name = mc.textField(text="")
		mc.rowColumnLayout(numberOfColumns=2)
		self.enable_pxr_layer_checkbox = mc.checkBox(label="PxrLayerSurface", width=self.window_width/4)
		self.menu = mc.optionMenu(label="Extension")
		mc.menuItem(label=".tif")
		mc.menuItem(label=".exr")
		mc.menuItem(label=".png")
		mc.menuItem(label=".jpg")
		self.create_shader_button = mc.button(label="CREATE SHADER",width=self.window_width,command=self.create_shader_function)
		mc.setParent("..")
		mc.setParent("..")"""
		#RANDOM LAMBERT CREATOR
		self.RandomLambertTool=mc.frameLayout(visible=False, parent=self.main_column, label="Random Lambert Tool", labelAlign="top", width=self.window_width, collapsable=True, collapse=True, backgroundColor=(0.138, 0.102, 0.224))
		mc.separator(style="none", height=10)
		mc.button(label="CREATE RANDOM LAMBERT", width=self.window_width/2, command=self.assign_random_lambert_function, parent=self.RandomLambertTool)



		#RANDOMIZE TOOL
		self.RandomizeTool = mc.frameLayout(visible=False, label="Randomize Tool", labelAlign="top", parent=self.main_column,width=self.window_width, collapsable=True, collapse=True, backgroundColor=(0.138, 0.102, 0.224))
		self.random_rowcol1 = mc.rowColumnLayout(numberOfColumns=2, columnWidth=(self.window_width/2, self.window_width/2), parent=self.RandomizeTool)
		mc.text(label="Min value", width=self.window_width/2, parent=self.random_rowcol1)
		mc.text(label="Max value", width=self.window_width/2, parent=self.random_rowcol1)
		self.min_value_field = mc.floatField(width=self.window_width/2, parent=self.random_rowcol1)
		self.max_value_field = mc.floatField(minValue=(mc.floatField(self.min_value_field, query=True, value=True)), parent=self.random_rowcol1, width=self.window_width/2)

		self.random_col1 = mc.columnLayout(adjustableColumn=True, parent=self.RandomizeTool)
		self.randomize_seed_button= mc.button(label="SEED", command=self.randomize_settings_function, parent=self.random_col1)
		#animation?
		#	--> enable delta settings		
		self.enable_delta_checkbox = mc.checkBox(label="Animation", onCommand=partial(self.randomize_animation_settings, True), parent=self.random_col1, offCommand=partial(self.randomize_animation_settings, False))
		self.delta_value = mc.optionMenu(label="Delta mode", width=self.window_width/2, enable=False, changeCommand=self.delta_mode_settings, parent=self.random_col1)
		mc.menuItem("Relative")
		mc.menuItem("Absolute")
		mc.separator(style="none", height=5)
		mc.text(label="Delta value", parent=self.random_col1)
		
		self.random_rowcol2 = mc.rowColumnLayout(numberOfColumns=2, parent=self.RandomizeTool, columnWidth=(self.window_width/2, self.window_width/2))
		mc.text(label="Min delta", parent=self.random_rowcol2)
		mc.text(label="Max delta", parent=self.random_rowcol2)
		self.min_delta_intfield = mc.intField(minValue=0, enable=False, parent=self.random_rowcol2)
		self.max_delta_intfield = mc.intField(minValue=1, enable=False, parent=self.random_rowcol2)
		
		self.random_rowcol3 = mc.rowColumnLayout(numberOfColumns=2, columnWidth=(self.window_width / 2, self.window_width / 2), parent=self.RandomizeTool)
		mc.text(label="Min key value", width=self.window_width/2, parent=self.random_rowcol3)
		mc.text(label="Max key value", width=self.window_width/2, parent=self.random_rowcol3)
		self.min_key_intfield = mc.intField(minValue = 1, width=self.window_width/2, enable=False, parent=self.random_rowcol3)
		self.max_key_intfield = mc.intField(minValue = 2, width=self.window_width/2, enable=False, parent=self.random_rowcol3)
		
		self.random_col2 = mc.columnLayout(adjustableColumn=True, parent=self.RandomizeTool)
		mc.separator(style="none", height=10)
		self.randomize_create_anim_button = mc.button(label="Create Animation", command=self.randomize_settings_function, enable=False, parent=self.random_col2)
		



		#REFERENCED LIGHT TOOL
		self.ReferencedLightsTool = mc.frameLayout(visible=False, label="Referenced Lights Tool", backgroundColor=(0.138, 0.102, 0.224), width=self.window_width, parent=self.main_column, collapsable=True, collapse=True)

		mc.text(label="Attributes", parent=self.ReferencedLightsTool)
		self.attributes_light_menu = mc.textScrollList(numberOfRows=7, allowMultiSelection=True, enable=True, append=self.list_light_attributes, parent=self.ReferencedLightsTool)


		mc.button(label="Define Color", enable=True, command=self.define_referenced_light_color_function, parent=self.ReferencedLightsTool)
		self.float_value = mc.floatField(parent=self.ReferencedLightsTool)
		mc.button(label="Apply Settings", parent=self.ReferencedLightsTool, command=self.change_referenced_light_settings_function)








	def create_shader_function(self, event):
		#get the selection
		#self.selection = mc.ls(sl=1, sn=True, showType=True)

		self.selection = mc.ls(sl=1, sn=True)
		self.selected_mesh = mc.filterExpand(sm=12)

		if self.selected_mesh == None:
			mc.error("You have to select a mesh to apply a texture")
			return
		#get the content of the textfield
		#check if the content is empty?
		self.content = mc.textField(self.shader_name, query=True, text=True)
		if self.letter_verification_function(mc.textField(self.shader_name, query=True, text=True)) == False:
			mc.error("You have to enter a name for the new shader!")
			return
		#check if the pxrlayersurface checkbox is enabled
		#if yes create a pxrlayersurface 
		#connect others nodes (an other functions?)
		
		
		
		if mc.checkBox(self.enable_pxr_layer_checkbox, query=True, value=True)==True:
			self.material = mc.shadingNode("PxrLayerSurface", n=self.content,asShader=True)
			layer_mixer = mc.shadingNode("PxrLayerMixer", asTexture=True)
			layer1 = mc.shadingNode("PxrLayer", asTexture=True)
			layer2 = mc.shadingNode("PxrLayer", asTexture=True)

			mc.connectAttr(layer1+".pxrMaterialOut", layer_mixer+".layer1")
			mc.connectAttr(layer2+".pxrMaterialOut", layer_mixer+".baselayer")
			mc.connectAttr(layer_mixer+".pxrMaterialOut", self.material+".inputMaterial")
		else:
			self.material = mc.shadingNode("PxrSurface", n=self.content, asShader=True,asTexture=True)

		shading_engine = mc.sets(name = "%sSG"%self.material, empty=True, renderable=True, noSurfaceShader=True)
		mc.connectAttr("%s.outColor" % self.material, "%s.surfaceShader" % shading_engine)

		for mesh in self.selected_mesh:
			mc.select(mesh)
			mc.hyperShade(assign=self.material)
		
				
		

		"""
		get the workspace path
		try to find the name of the texture inside the sourceimages folder
		take a list of texture name and if those texture exists as files load them inside a pxrtexture

		albedo - diffuse color
		roughness  - remap - specular roughness
		bump - bump 
		displace
		refraction - refraction gain
		reflection - reflection gain
		diffusegain - diffuse gain
		mask - pxrlayer surface
		"""
		#CHECK THE INDEX OF THE FILE
		#BETWEEN ALBEDO 1 / ALBEDO 2 / ALBEDO ... / ALBEDO 3
		#the program will choose albedo 3
		self.workspace = mc.workspace(query=True, rd=True)
		#check if the folder sourceimages exists
		if os.path.isdir(self.workspace + "/sourceimages/")==False:
			mc.error("Maya can't find the sourceimages folder in your project!")
			return
		#check if there is a folder inside the project called with the texturename
		self.sourceimages = self.workspace + "sourceimages/"
		print(self.sourceimages + self.content)
		if os.path.isdir(self.sourceimages + self.content)==False:
			mc.error("Shader created - no texture found in the project!")
			return 
		else:
			self.shader_path = self.sourceimages + self.content + "/"
			"""
			part of the tool that search for the differents textures
			"""
			#creation of the final shader list
			#note for others programmers 
			#it's possible to do the creation of the final list and the real shader creation (pxrremap, pxrtexture...) in
			#only one while, it's just a bit more tricky to do and for now i'm too lazy to do it
			#it take more power but it's more understandable for me
			
			self.folder_content = next(walk(self.shader_path), (None, None, []))[2]
			self.shader_file_list = []
			self.final_shader_file_list = []
			self.default_extension = mc.optionMenu(self.menu,query=True, value=True)
			
			#try to find all the files with the right extensions
			for element in self.folder_content:
				if (os.path.splitext(element)[1]) == self.default_extension:
					self.shader_file_list.append(element)
					
			#try the last index of each categorie
			for element in self.file_type:
				#take only the name of the file and try to split by _
				filecategorie = ((os.path.splitext(element)[0]).split("_"))[0]
				i = 1
				while True:
					if os.path.isfile(self.shader_path+element+"_"+str(i)+self.default_extension)==False:
						if (i - 1) != 0:
							self.final_shader_file_list.append(self.shader_path+element+"_"+str(i - 1)+self.default_extension)
						break
						
					i+=1

			#try to create a pxrtexture for each item, and load the associated file in it
			for element in self.final_shader_file_list:
				pxr_texture = mc.shadingNode("PxrTexture", asTexture=True)
				mc.setAttr(pxr_texture+".filename", element, type="string")

				basename = (os.path.splitext(os.path.basename(element))[0]).split("_")[0]
				#DISABLE THE MASK FOR PXRLAYERSURFACE AT THE BEGINNING
				if mc.checkBox(self.enable_pxr_layer_checkbox, query=True, value=True)==True:
					mc.setAttr(layer_mixer+".layer1Enabled",0)

				#ALBEDO FILE
				if basename == "albedo":
					mc.setAttr(pxr_texture+".linearize", 1)
					if mc.checkBox(self.enable_pxr_layer_checkbox, query=True, value=True)==False:
						mc.connectAttr(pxr_texture+".resultRGB",self.material+".diffuseColor")					
					if mc.checkBox(self.enable_pxr_layer_checkbox, query=True, value=True)==True:
						mc.connectAttr(pxr_texture+".resultRGB",layer2+".diffuseColor")

				#ROUGHNESS FILE
				if basename == "roughness":
					remap = mc.shadingNode("PxrRemap", asTexture=True)
					mc.connectAttr(pxr_texture+".resultRGB", remap+".inputRGB")
					if mc.checkBox(self.enable_pxr_layer_checkbox, query=True, value=True)==False:
						mc.connectAttr(remap+".resultRGB.resultRGBR",self.material+".specularRoughness")					
					if mc.checkBox(self.enable_pxr_layer_checkbox, query=True, value=True)==True:
						mc.connectAttr(remap+".resultRGB.resultRGBR",layer2+".specularRoughness")

				#BUMP FILE
				if basename == "bump":
					bump = mc.shadingNode("PxrBump", asTexture=True)
					mc.setAttr(pxr_texture+".linearize",1)
					mc.connectAttr(pxr_texture+".resultRGB.resultRGBR", bump+".inputBump")
					if mc.checkBox(self.enable_pxr_layer_checkbox, query=True, value=True)==False:
						mc.connectAttr(bump+".resultN",self.material+".bumpNormal")					
					if mc.checkBox(self.enable_pxr_layer_checkbox, query=True, value=True)==True:
						mc.connectAttr(bump+".resultN",layer2+".bumpNormal")

				#MASK FILE
				if basename == "mask":
					remap2 = mc.shadingNode("PxrRemap", asTexture=True)
					mc.connectAttr(pxr_texture+".resultRGB", remap2+".inputRGB")					
					if mc.checkBox(self.enable_pxr_layer_checkbox, query=True, value=True)==True:
						mc.setAttr(layer_mixer+".layer1Enabled",1)
						mc.connectAttr(remap2+".resultR",layer_mixer+".layer1Mask")

			print("TEXTURE SUCCESSFULLY CREATED!")








	def assign_random_lambert_function(self, event):
		#get the list of meshes
		self.selected_mesh = mc.filterExpand(sm=12)
		if self.selected_mesh==None:
			mc.error("You have to select at least one mesh!")
			return
		#loop that assign a new lambert for each mesh selected with a random color for each
		for mesh in self.selected_mesh:
			material_name = "%s_lambert" % mesh 
			material = mc.shadingNode("lambert",name=material_name, asShader=True)
			shading_node = mc.sets(name = "%sSG"%material, empty=True, renderable=True, noSurfaceShader=True)

			mc.connectAttr("%s.outColor"%material, "%s.surfaceShader"%shading_node)

			mc.select(mesh)
			mc.hyperShade(assign=material)
			mc.setAttr(material+".color", random.uniform(0,1), random.uniform(0,1), random.uniform(0,1))









	def define_referenced_light_color_function(self,event):
		mc.colorEditor()
		self.selected_color = mc.colorEditor(query=True, rgb=True)
		print(self.selected_color)



	def change_referenced_light_settings_function(self, event):
		#get and check all informations
		"""
		get the list of all the files in the project
		get the list of all the selected lights that are in referenced files of the project
		get the selected attributes list
		"""

		#check the attributes selection
		#if none, stop the function
		selected_attributes = mc.textScrollList(self.attributes_light_menu, query=True, si=True)
		if selected_attributes == None:
			mc.error("You have to select at least 1 attribute to change")
			return
		print(selected_attributes)
		float_content = mc.floatField(self.float_value, query=True, value=True)


		project_files = mc.file(query=True, list=True)
		selection = pm.listRelatives(mc.ls(sl=True))
		selection_name = mc.ls(sl=True, sn=True)
		#keep only lights
		type_list = []
		shape_list = []
		name_list = []
		real_name_list = []
		for x in range(0, len(selection)):
			if (pm.objectType(selection[x]) in self.list_light_kind)==True:
				name_list.append(selection_name[x])
				shape_list.append(selection[x])
				type_list.append(pm.objectType(selection[x]))



		#check in all referenced files if those lamps exists
		referenced_files = pm.listReferences()
		#delete the name of the file inside the name of the item
		for file in referenced_files:
			for i in range(0, len(name_list)):
				if (name_list[i].split(":")[0]) == file.namespace:
					name_list[i] = name_list[i].split(":")[1]
				if (shape_list[i].split(":")[0]) == file.namespace:
					shape_list[i] = shape_list[i].split(":")[1]
		print("Lamp Selected")

		
		"""
		for each lamp
		check if it exist
			if yes
				finish the action then continue
			else:
				continue
		"""	
		for i in range(0, len(name_list)):	
			for file in referenced_files:
			

				#check if the file is a .ma file
				if os.path.splitext(file.path)[1] != ".ma":
					mc.warning("%s isn't a .ma file" % file.path)
					break
				else:
					#take the content of the file
					content = []
					light_content = []
					line_ini_light = 'createNode %s -n "%s" -p "%s";\n' % (type_list[i], shape_list[i], name_list[i])

					with open(file.path, "r") as read_file:
						for line in read_file.readlines():
							content.append(line)

					#setAttr ".lightColor" -type "float3" 1 1 1 ;
					#take only the part that concern the current light
					for y in range(0, len(content)):
						if content[y] == line_ini_light:
							#print("CHECK %s" %name_list[i])
							light_content.append(content[y])

							#then add the whole content of THIS light only
							#and stop when it's an other createNode part
							for z in range(y+1, len(content)):
								if ("createNode" in content[z]) == True:
									break
								#change the value of lines inside the content list
								#go through the selected attributes list
								for attr in selected_attributes:
									splited = content[z].split(" ")
									if (splited[0] == "\tsetAttr") and (splited[1] == '".%s"' % attr):
										if attr == "lightColor":
											print("color changed!")
											content[z] = '\tsetAttr ".%s" -type "float3" %s %s %s ;\n' % (attr, self.selected_color[0], self.selected_color[1], self.selected_color[2])
										else:
											#change the line
											content[z] = '\tsetAttr ".%s" %s;\n' % (attr, float_content)
										print("Line changed %s : %s" % (file, attr))

				
					with open(file.path, "w") as save_new_file:
						for line in content:
							save_new_file.write(line)

		print("Informations saved")
		#reload referenced
		for file in referenced_files:
			mc.file(file.path, loadReference=True)
		mc.warning("Reference changed successfully!")













	def randomize_animation_settings(self, status, event):
		if status == True:
			mc.button(self.randomize_seed_button, edit=True, enable=False)
		else:
			mc.button(self.randomize_seed_button, edit=True, enable=True)
		mc.optionMenu(self.delta_value, edit=True, enable=status)
		mc.button(self.randomize_create_anim_button, edit=True, enable=status)
		mc.intField(self.min_delta_intfield, edit=True, enable=status)
		mc.intField(self.max_delta_intfield, edit=True, enable=status)
		mc.intField(self.min_key_intfield, edit=True, enable=status)
		mc.intField(self.max_key_intfield, edit=True, enable=status)


	def delta_mode_settings(self, event):
		if mc.optionMenu(self.delta_value, q=True, value=True)=="Relative":
			mc.intField(self.min_delta_intfield, edit=True, enable=True)
		else:
			mc.intField(self.min_delta_intfield, edit=True, enable=False)



	def randomize_settings_function(self, event):
		"""
		check the len of selected attributes len
		check if animation is enable or not?
			-> yes -> create the whole animation
			-> no -> create a key for the current frame
		"""
		channelBox = mel.eval("global string $gChannelBoxName; $temp=$gChannelBoxName;")
		attrs1 = mc.channelBox(channelBox, query=True, sma=True)
		attrs2 = mc.channelBox(channelBox, query=True, ssa=True)

		if (attrs1==None) and (attrs2==None):
			mc.error("You have to select at least one attribute in the ChannelBox")
			return
		

		

		#take ui values
		min_value = mc.floatField(self.min_value_field, q=True, value=True)
		max_value = mc.floatField(self.max_value_field, q=True, value=True)

		min_delta = mc.intField(self.min_delta_intfield, q=True, value=True)
		max_delta = mc.intField(self.max_delta_intfield, q=True, value=True)
		delta_mode = mc.optionMenu(self.delta_value, query=True, value=True)

		if (min_value >= max_value) or (min_delta >= max_delta):
			mc.error("Min / Max value error")
			return
		#take the selection
		outliner_selection = mc.ls(sl=True, sn=True)

		
		#creation of loops to apply keys and randomness
		for item in outliner_selection:
			if attrs1 != None:
				print(attrs1)
				for attr in attrs1:
					if mc.checkBox(self.enable_delta_checkbox, query=True, value=True)==False:
						#put the random value in each attribute
						value = uniform(min_value, max_value)
						mc.setAttr(item+"."+attr, value)
						#mc.setKeyframe(item, attribute=attr, v=value, t=mc.currentTime(query=True))
					else:
						min_frame = mc.intField(self.min_key_intfield, query=True, value=True)
						max_frame = mc.intField(self.max_key_intfield, query=True, value=True)
						
						min_delta = mc.intField(self.min_delta_intfield, query=True, value=True)
						max_delta = mc.intField(self.max_delta_intfield, query=True, value=True)
						i = min_frame
						while i < (max_frame):
							mc.setKeyframe(item, attribute=attr, v=uniform(min_value, max_value), t=i)
							
							if mc.optionMenu(self.delta_value, query=True, value=True)=="Relative":
								delta = randrange(min_delta, max_delta)
								i += delta
							else:
								i+= max_delta

			if attrs2 != None:
				print(attrs2)
				for attr in attrs2:
					if mc.checkBox(self.enable_delta_checkbox, query=True, value=True)==False:
						#put the random value in each attribute
						value = uniform(min_value, max_value)
						mc.setAttr(item+"."+attr, value)
						#mc.setKeyframe(item, attribute=attr, v=value, t=mc.currentTime(query=True))
					else:
						min_frame = mc.intField(self.min_key_intfield, query=True, value=True)
						max_frame = mc.intField(self.max_key_intfield, query=True, value=True)
							
						min_delta = mc.intField(self.min_delta_intfield, query=True, value=True)
						max_delta = mc.intField(self.max_delta_intfield, query=True, value=True)
						i = min_frame
						while i < (max_frame):
							mc.setKeyframe(item, attribute=attr, v=uniform(min_value, max_value), t=i)
								
							if mc.optionMenu(self.delta_value, query=True, value=True)=="Relative":
								delta = randrange(min_delta, max_delta)
								i += delta
							else:
								i+= max_delta





	

	
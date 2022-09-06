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
		# Global Variables
		self.shape_holder = [ "transform", "joint"]
		self.shapes = [ "mesh", "nurbsCurve", "nurbsSurface", "locator" ]
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
		self.attribute_informations = []
		self.attribute_list = [
			"visibility", 
			"follow"
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

		self.clavicule_locator = None 
		self.shoulder_jnt_ctrl = []


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
		mc.button(label="Import Item", command=partial(self.import_curve_function, "manual"), parent=self.create_controller_left_column)

		#RIGHT COLUMN CREATE CONTROLLERS
		"""
		Create controller tool
			-> create a locator
			-> or select a locator
			-> validation button to create the controller since you have 
				a locator selected
			-> import saved curve checkbox (take the seleciton in textscrolllist)
			-> can select several locators

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
		mc.separator(style="none", height=5, parent=self.create_controller_right_column)

		mc.text(label="Builder instanced attributes name", parent=self.create_controller_right_column)
		self.instanced_attribute_name_ui = mc.textField(parent=self.create_controller_right_column)
		self.instanced_attribute_color_ui = mc.colorIndexSliderGrp(min=1, max=31, value=1, parent=self.create_controller_right_column)
		mc.button(label="Create builder instanced attributes", command=self.build_instanced_attributes_function, parent=self.create_controller_right_column)
		mc.separator(style="none", parent=self.create_controller_right_column, height=10)

		self.joints_on_surfaces_frame = mc.frameLayout(label="Joints on surfaces", labelAlign="top", width=self.window_width/2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.create_controller_right_column)
		#creates joints on surfaces
		mc.text(label="Number of joints", parent=self.joints_on_surfaces_frame)
		self.jnt_number_ui = mc.intField(minValue=1, parent=self.joints_on_surfaces_frame)
		self.jnt_axe_ui = mc.optionMenu(label="Joints axe", parent=self.joints_on_surfaces_frame)
		mc.menuItem(label="U")
		mc.menuItem(label="V")
		mc.button(label="Create joints on surfaces", parent=self.joints_on_surfaces_frame, command=self.check_joints_creation_on_surfaces)
		mc.separator(style="none", parent=self.joints_on_surfaces_frame, height=19)


		self.spline_controller_frame = mc.frameLayout(label="SplineNeckHips Auto Rig", labelAlign="top", width=self.window_width/2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.create_controller_right_column)
		mc.text(label="Spline Controller Color", parent=self.spline_controller_frame)
		self.spline_controller_fk_color_ui = mc.colorIndexSliderGrp(min=1, max=31, value=1, parent=self.spline_controller_frame)
		#create an ik hierarchy
		self.spline_controller_ik_checkbox = mc.checkBox(label="Ik hierarchy", value=True, changeCommand=self.enable_spline_controller_ik_color_function)
		self.spline_controller_ik_color_ui = mc.colorIndexSliderGrp(min=1, max=31, value=1, parent=self.spline_controller_frame, enable=True)
		mc.button(label="Create Spline and Neck Rig", command=self.create_spline_function, parent=self.spline_controller_frame)
		self.spline_instanced_attribute_color_ui = mc.colorIndexSliderGrp(min=1, max=31, value=1, parent=self.spline_controller_frame)



		self.clavicule_controller_frame = mc.frameLayout(label="Clavicule Auto Rig", labelAlign="top", width=self.window_width/2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.create_controller_right_column)
		#ask for the joint or locator to control
		mc.button(label="Define clavicule locator", parent=self.clavicule_controller_frame, command=self.define_clavicule_locator_function)
		mc.button(label="Define shoulder joint and controller", parent=self.clavicule_controller_frame, command=self.define_shoulder_jnt_ctrl_function)
		mc.button(label="Orient clavicule locator", parent=self.clavicule_controller_frame, command=self.orient_clavicule_locator_function)
		self.clavicule_controller_color_ui = mc.colorIndexSliderGrp(min=1, max=31, value=1, parent=self.clavicule_controller_frame)
		mc.button(label="Create clavicule hierarchy", parent=self.clavicule_controller_frame, command=self.create_clavicule_hierarchy_function)




		self.neck_head_controller_frame = mc.frameLayout(label="Neck Head auto Rig", labelAlign="top", width=self.window_width/2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.create_controller_right_column)
		#create neck controller and head controller
		#define the color of the controller
		self.neck_head_controller_color_ui = mc.colorIndexSliderGrp(min=1, max=31, value=1, parent=self.neck_head_controller_frame)
		self.neck_head_checkbox_ui = mc.checkBox(label="Parented Hierarchy", value=False)
		self.neck_head_follow_head_ui = mc.checkBox(label="Follow neck attribute", value=True)
		mc.button(label="Create neck and head controller", parent=self.neck_head_controller_frame, command=self.create_neck_head_function)



		self.attribute_frame = mc.frameLayout(label="Attribute Creator", labelAlign="top", width=self.window_width / 2, collapsable=True, collapse=True, backgroundColor=(0.192, 0.352, 0.350), parent=self.create_controller_right_column)
		mc.text(label="Attributes list", parent=self.attribute_frame)
		self.attribute_list_ui = mc.textScrollList(numberOfRows=15, parent=self.attribute_frame, allowMultiSelection=True, append=self.attribute_list)
		#button to define the item that will receive the attribute
		#button to define targets of the attribute
		self.attribute_name_ui = mc.textField(parent=self.attribute_frame)
		mc.button(label="Define the builder attribute", command=self.define_attribute_builder, parent=self.attribute_frame)
		mc.button(label="Define informations elements", command=self.define_information_attribute, parent=self.attribute_frame)
		mc.button(label="Define targets of the attributes", command=self.define_attribute_target, parent=self.attribute_frame)
		mc.button(label="CREATE ATTRIBUTE", command=self.apply_attribute_function, parent=self.attribute_frame)


		mc.separator(style="singleDash", height=15, parent=self.create_controller_frame)
		mc.button(label="CREATE HOOK", parent=self.create_controller_frame, command=self.create_hook_function)
		mc.separator(style="none", height=15, parent=self.create_controller_frame)







	





		mc.showWindow()







	def create_neck_head_function(self, event):
		#check the locator selection
		locator_selection = [obj for obj in cmds.ls(sl=True) if cmds.listRelatives(obj, shapes=True, type="locator")]
		if (locator_selection == None) or (len(locator_selection) == 0):
			mc.error("You have to select locators!")
			return
		#check the saved curve
		if self.ctrl_fk_curve == None:
			mc.error("You have to define a curve!")
			return
		"""
		for new versions create an option to make:
			parented hierarchy
			unparented hierarchy
		"""
		#create the hierarchy for the two controllers
		created_curve = []
		root_list = []

		neck_head_transform = mc.createNode("transform", n="ctrls_neck_head", parent=None)
		#UNPARENTED HIERARCHY
		if mc.checkBox(self.neck_head_checkbox_ui, query=True, value=True)==False:
			for locator in locator_selection:
				new_curve, new_root = self.create_controller_function([locator], "neck_head")
				created_curve = created_curve + new_curve
				root_list = root_list + new_root
			#parent all roots in the same transform
			for root in root_list:
				mc.parent(root, neck_head_transform)
		#PARENTED HIERARCHY
		else:
			created_curve, root_list = self.create_controller_function(locator_selection, "neck_head")
			mc.parent(root_list[0], neck_head_transform)

		"""
		hook loc_info_head to root_head
		parent constraint loc_info_head to neck controller
		"""

		#color the curve
		for curve in created_curve:
			self.color_curve_function(curve, int(mc.colorIndexSliderGrp(self.neck_head_controller_color_ui, query=True, value=True)) - 1)


	def create_clavicule_hierarchy_function(self, event):
		"""
		create the hierarchy with the clavicule joint inside
		hook the shoulder curve to the clavicule controller
		"""
		#check the content of all variables
		if self.clavicule_locator == None:
			mc.error("You have to define a clavicule locator!")
			return
		if len(self.shoulder_jnt_ctrl)==0:
			mc.error("You have to define the shoulder joint and controller!")
			return
		else:
			#get the color 
			color = mc.colorIndexSliderGrp(self.clavicule_controller_color_ui, query=True, value=True)
			created_curve = self.create_controller_function([self.clavicule_locator], "clavicule_controller")
			for controller in created_curve:
				self.color_curve_function(controller, int(color)-1)
				#create a maintain offset parent constraint between clavicule controller 
				#(created curve) and the shoulder joint
				mc.parentConstraint(created_curve, self.shoulder_jnt_ctrl[0], maintainOffset=True, skipRotate=["x", "y", "z"])
			
	def orient_clavicule_locator_function(self, event):
		#check if the clavicule locator and shoulder joint exist
		if self.clavicule_locator == None:
			mc.error("You have to define the clavicule locator!")
			return
		if len(self.shoulder_jnt_ctrl) == 0:
			mc.error("You have to define the shoulder joint / controller!")
			return
		#aim constraint the locator to shoulder joint
		aim_constraint = mc.aimConstraint(self.shoulder_jnt_ctrl[0], self.clavicule_locator)
		mc.delete(aim_constraint)
		mc.warning("Clavicule locator oriented to the shoulder locator!")
		return

	def define_shoulder_jnt_ctrl_function(self, event):
		#get the selection
		#one controller and one joint
		selection = mc.ls(sl=True)
		if (selection == None) or (len(selection) != 2):
			mc.error("You have to select only one joint and one controller!")
			return
		controller_selection = mc.filterExpand(sm=9)[0]
		if controller_selection == None:
			mc.error("You have to select one controller!")
			return
		joint_selection = None
		for element in selection:
			if mc.objectType(element)=="joint":
				joint_selection = element
		if joint_selection == None:
			mc.error("You have to select one joint!")
			return 
		self.shoulder_jnt_ctrl = [joint_selection, controller_selection]
		mc.warning("Shoulder joint and controller defined successfully!")
		return

	def define_clavicule_locator_function(self, event):
		#get the selection
		#check that the selection is a locator
		if (mc.ls(sl=True, sn=True)==None) or (len(mc.ls(sl=True, sn=True)) > 1):
			mc.error("You have to select one locator!")
			return
		else:
			
			if mc.objectType(mc.listRelatives(mc.ls(sl=True), children=True)[0])=="locator":
				self.clavicule_locator = mc.ls(sl=True, sn=True)[0]
				mc.warning("Locator defined successfully!")
				return
			else:
				mc.error("You have to select only one locator")
				return

	def create_hook_surface(self, sel=[], UVs=[], reset=True):
	    """
	    Usage :
	        - Select one nurbSurface
	        - ( Select one or several child(ren) )
	    """
	    # Variables
	    surface, tr_surface, children = self.filter_surface_and_children( sel )
	    
	    name = self.get_sn( tr_surface )
	    if children:
	        child_name = self.get_sn( children[0] )
	        name += f"_for_{child_name}"
	        
	    #   ( Get UVs from child )
	    
	    # Create the hook
	    hook = cmds.createNode( "transform", name="hook_"+name, skipSelect=True )
	    
	    # Lock Transform's Attributes
	    self.lock_transforms_attrs_to_default( hook, attrs=["scale", "shear"] )
	    cmds.setAttr( hook+".inheritsTransform", True, lock=True )
	    
	    # Create nodes
	    posi = cmds.createNode( "pointOnSurfaceInfo", n="posi_"+name, ss=True )
	    fbfmx = cmds.createNode( "fourByFourMatrix", n="fbfmx_"+name, ss=True )
	    mmx = cmds.createNode( "multMatrix", n="mmx_"+name, ss=True )
	    dmx = cmds.createNode( "decomposeMatrix", n="dmx_"+name, ss=True )
	    
	    # Connections
	    #   surface -> posi
	    cmds.connectAttr( surface+".worldSpace[0]", posi+".inputSurface" )
	    #   posi -> fbfmx
	    attrs = ["normalizedNormal", "normalizedTangentU", "normalizedTangentV", "position"]
	    axes = ["X", "Y", "Z"]
	    for i in range( len( attrs ) ):
	        attr = attrs[i]
	        for j in range( len( axes ) ):
	            axis = axes[j]
	            cmds.connectAttr( f"{posi}.{attr}{axis}", f"{fbfmx}.in{i}{j}" )
	    #   fbfmx -> mmx
	    cmds.connectAttr( fbfmx+".output", mmx+".matrixIn[0]" )
	    #   mmx -> dmx
	    cmds.connectAttr( mmx+".matrixSum", dmx+".inputMatrix" )
	    #   dmx -> hook
	    self.connect_dmx_to_tr( [dmx, hook], attrs=["translate", "rotate"] )
	        
	    #   hook -> mmx
	    cmds.connectAttr( hook+f".parentInverseMatrix[0]", mmx+f".matrixIn[1]" )
	    
	    # SetAttrs UVs
	    if not UVs:
	        if children:
	            child = children[0]
	            tmp_dmx = cmds.createNode( "decomposeMatrix", ss=True )
	            tmp_cpos = cmds.createNode( "closestPointOnSurface", ss=True )
	            cmds.connectAttr( child+".worldMatrix[0]", tmp_dmx+".inputMatrix" )
	            cmds.connectAttr( tmp_dmx+".outputTranslate", tmp_cpos+".inPosition" )
	            cmds.connectAttr( surface+".worldSpace[0]", tmp_cpos+".inputSurface" )
	            parameterU = cmds.getAttr( tmp_cpos+".result.parameterU" )
	            parameterV = cmds.getAttr( tmp_cpos+".result.parameterV" )
	            UVs = [ parameterU, parameterV ]
	            cmds.delete( tmp_dmx, tmp_cpos )
	        else:
	            UVs = [ 0.0, 0.0 ]
	    cmds.setAttr( posi+".parameterU", UVs[0] )
	    cmds.setAttr( posi+".parameterV", UVs[1] )
	    
	    # ( Parent the hook to firstChild's parent )
	    if children:
	        parents = cmds.listRelatives( children[0], p=True, path=True )
	        if parents:
	            hook = cmds.parent( hook, parents[0] )[0]
	    
	    # ( Parent children to the hook )
	    if children:
	        children = cmds.parent( children, hook )
	        if reset:
	            self.reset_transforms( children )
	    
	    return hook

	def check_joints_creation_on_surfaces(self, event):
		#get the selection
		joints_number = mc.intField(self.jnt_number_ui, query=True, value=True)
		joints_axe = mc.optionMenu(self.jnt_axe_ui, query=True, value=True)
		#check the selection
		selection = mc.filterExpand(sm=10)
		if sel == None:
			mc.error("You have to select surfaces!")
			return
		#call the create jnts and hooks on surfaces function
		self.create_jnts_and_hooks_on_surfaces(sel=selection, nb_joints=joints_number, UV_line=joints_axe)

	def create_jnts_and_hooks_on_surfaces(self, sel=[], nb_joints=5, UV_line="U" ):
	    sel = self.filter_sel( sel )
	    
	    UV_line = UV_line.upper()
	    if UV_line not in ["U","V"]:
	        cmds.error( "Please use 'U' or 'V' as UV_line" )
	    
	    surfaces = []
	    for obj in sel:
	        obj_type = cmds.objectType( obj )
	        if obj_type in ["transform", "joint"]:
	            tmp_surfaces = cmds.listRelatives( obj, shapes=True, type="nurbsSurface", noIntermediate=True, path=True )
	            if tmp_surfaces:
	                surfaces += tmp_surfaces
	        elif obj_type == "nurbsSurface":
	            surfaces.append( obj )
	            
	    sks_groups = []
	    for surface in surfaces:
	        tr_surface = self.get_transform( surface )
	        tr_surface_name = self.get_sn( tr_surface )
	        
	        sks_group = cmds.createNode( "transform", n="sks_"+tr_surface_name, ss=True )
	        
	        u_max = cmds.getAttr( surface+f".minMaxRangeU.maxValueU" )
	        v_max = cmds.getAttr( surface+f".minMaxRangeV.maxValueV" )
	        if UV_line == "U":
	            u_value = u_max / (nb_joints-1)
	            v_value = v_max / 2.0
	        if UV_line == "V":
	            u_value = u_max / 2.0
	            v_value = v_max / (nb_joints-1)
	        
	        hooks = []
	        for i in range( nb_joints ):
	            jnt_name = f"sk_{tr_surface_name}_{i}"
	            if i == (nb_joints-1):
	                jnt_name = f"end_{tr_surface_name}_{i}"
	            jnt = cmds.createNode( "joint", name=jnt_name, ss=True, parent=sks_group )
	            
	            if UV_line == "U":
	                UVs = [ u_value * i, v_value ]
	            elif UV_line == "V":
	                UVs = [ u_value, v_value * i ]
	                
	            hooks.append( self.create_hook_surface( [jnt, surface], UVs=UVs ) )
	        
	        sks_groups.append( sks_group )
	    
	    return sks_groups

	def filter_surface_and_children(self, sel=[] ):
	    sel = self.filter_sel( sel )
	    surface = ""
	    children = []
	    #   Filter Surface and Children
	    for obj in sel:
	        obj_type = cmds.objectType( obj )
	        if obj_type in ["transform", "joint"]:
	            surfaces = cmds.listRelatives( obj, shapes=True, type="nurbsSurface", noIntermediate=True, path=True )
	            if surfaces:
	                surface = surfaces[0]
	            else:
	                children.append( obj )
	        elif obj_type == "nurbsSurface":
	            surface = obj    
	    if not surface:
	        cmds.error( "Have to select at least one surface" )
	    tr_surface = self.get_transform( surface )
	        
	    return surface, tr_surface, children

	def lock_transforms_attrs_to_default( self, sel=[], attrs=["translate", "rotate", "scale", "shear"] ):
	    sel = self.filter_sel( sel )
	    for obj in sel:
	        for attr in attrs:
	            value = 0
	            all_axis = ["X", "Y", "Z"]
	            if attr == "scale":
	                value = 1
	            elif attr == "shear":
	                all_axis = ["XY", "XZ", "YZ"]
	            for axis in all_axis:
	                cmds.setAttr( obj+"."+attr+axis, value, lock=True )

	def connect_dmx_to_tr( self, sel=[], attrs=["translate", "rotate", "scale", "shear" ] ):
	    dmx = self.filter_sel( sel, filter_types="decomposeMatrix" )[0]
	    children = self.filter_sel( sel, filter_types=self.shape_holder )
	    if type( attrs ) is not list:
	        attrs = [attrs]
	    for child in children:
	        for attr in attrs:
	            cmds.connectAttr( f"{dmx}.output{attr.title()}", f"{child}.{attr}" )

	def reset_transforms( self, sel=[], attrs=["translate", "rotate", "scale", "shear"] ):
	    sel = self.filter_sel( sel )
	    for obj in sel:
	        for attr in attrs:
	            value = 0
	            if attr == "scale":
	                value = 1
	            axes = ["X", "Y", "Z"]
	            if attr == "shear":
	                axes = ["XY", "XZ", "YZ"]
	            for axis in axes:
	                cmds.setAttr( f"{obj}.{attr}{axis}", value )

	def filter_sel( self, sel=[], filter_types=[], filter_prefixes=[], filter_suffixes=[] ):
	    if not sel:
	        sel = cmds.ls( selection=True, allPaths=True )
	    elif type(sel) is not list:
	        sel = [sel]
	        
	    # Filtering
	    #   Filter by Node Types
	    sel = cmds.ls( sel, ap=True, type=filter_types )
	    
	    #   Filter by prefixes
	    if filter_prefixes:
	        if type( filter_prefixes ) is not list:
	            filter_prefixes = [filter_prefixes]
	        sel = [ x for x in sel if x.split("_")[0] in filter_prefixes ]
	    if filter_suffixes:
	        if type( filter_suffixes ) is not list:
	            filter_suffixes = [filter_suffixes]
	        sel = [ x for x in sel if x.split("_")[-1] in filter_suffixes ]
	            
	    return sel

	def define_attribute_builder(self, event):
		selection = mc.ls(sl=True, sn=True)
		self.attribute_builder = selection 

	def define_information_attribute(self, event):
		selection = mc.ls(sl=True, sn=True)
		self.attribute_informations = selection

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
					mc.connectAttr( "%s.%s" % (mc.listRelatives(builder, children=True)[0], new_attr), "%s.inFloat" % (float_constant) )
					mc.connectAttr("%s.outFloat"%(float_constant), "%s.visibility"%(self.attribute_target[0]))

				if attr == "follow":
					#check if two differents are selected
					if len(self.attribute_target) != 1:
						mc.error("You have to select only one target!")
						return
					if (self.attribute_informations == None) or (len(self.attribute_informations) != 1):
						mc.error("You have to define an informations node to follow")
						return
					#creation of the attribute
					mc.addAttr((mc.listRelatives(builder, children=True))[0], longName="follow_%s" % self.attribute_target[0], attributeType="float", minValue=0, maxValue=10, keyable=True)
					#creation of the fac attribute
					new_attr = "follow_%s"%self.attribute_target[0]
					mult_double_linear = mc.createNode("multDoubleLinear", n="facAttr_for_%s_%s"%(attr, self.attribute_target[0]))
					pair_blend = mc.createNode("pairBlend", n="pb_for_%s_%s"%(attr, self.attribute_target[0]))
					#modification of pair blend from euler to quaternions
					mc.setAttr("%s.rotInterpolation"%pair_blend,1)
					mc.setAttr("%s.input2"%mult_double_linear, 0.1)
					#creation of connexion between nodes
					mc.connectAttr("%s.%s"%(mc.listRelatives(builder, children=True)[0], new_attr), "%s.input1"%mult_double_linear)
					mc.connectAttr("%s.output"%(mult_double_linear), "%s.weight"%pair_blend)
					mc.connectAttr("%s.outRotate"%pair_blend, "%s.rotate"%self.attribute_target[0])
					mc.connectAttr("%s.translate"%self.attribute_informations[0], "%s.translate"%self.attribute_target[0])
					mc.connectAttr("%s.rotate"%self.attribute_informations[0], "%s.inRotate2"%pair_blend)
				mc.warning("Attribute created successfully!")
				return

	def color_curve_function(self, curve, color):
		mc.setAttr("%s.overrideEnabled"%curve, 1)
		mc.setAttr("%s.overrideColor"%curve, color)

	def build_instanced_attributes_function(self, event):
		attribute_name = mc.textField(self.instanced_attribute_name_ui, query=True, text=True)
		#letter verification
		if self.letter_verification_function(attribute_name)==False:
			mc.error("You have to define a name for this builder instanced attribute!")
			return
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
			created_curve = self.import_curve_function("spline_attribute_creation", "event")
			#color the created curve
			
			self.ctrk_fk_curve = None
			#put this curve in the first transform of the preset hierarchy
			h_node_list = self.hierarchy_preset[0]
			h_name_list = self.hierarchy_preset[1]

			
			for i in range(0, len(h_node_list)):
				if h_node_list[i] == "transform":
					root = mc.createNode("transform", n="%s_%s"% (h_name_list[i], attribute_name))
					print(created_curve, root)
					mc.parent(created_curve, root)
					break
			for i in range(0, len(h_node_list)):
				if h_node_list[i] == "curve":
					try:
						created_curve = mc.rename(created_curve, "%s_%s" % (h_name_list[i], attribute_name))
						self.color_curve_function(created_curve, int(mc.colorIndexSliderGrp(self.instanced_attribute_color_ui, query=True, value=True))-1)
						mc.scale(6, 6, 6, created_curve, componentSpace=True, scaleXY=True)
						break
					except:
						pass

			#create a locator
			#locator_t = mc.createNode("locator", n="builder_instanced_%s" % (attribute_name))
			locator_s = mc.createNode("locator")
			locator_t = mc.listRelatives(locator_s, parent=True)
			locator_s = mc.rename(locator_s, "instanced_attributes_%s_shape"%attribute_name)
			locator_t = mc.rename(locator_t, "builder_instanced_attributes_%s"%attribute_name)

			#hide all the attributes of the locator transform
			for attr in mc.listAttr(locator_s, channelBox=True, visible=True):
				mc.setAttr("%s.%s"%(locator_s, attr), keyable=False, channelBox=False)

			#create a separation attribute on the locator
			mc.addAttr(locator_s, longName="separator1", niceName="---|%s|---"%attribute_name.replace("attributes_", ""), attributeType="enum", keyable=True, hidden=False, enumName="-------------")
			mc.warning("Spline created!")
			#create a transform to put the instanced attribute inside
			instanced_attribute_transform = mc.createNode("transform", parent=None)
			mc.parent(locator_t, instanced_attribute_transform)
			mc.rename(instanced_attribute_transform, "builder_instanced_attributes_%s" % attribute_name)
			mc.warning("Builder instanced attributes created successfully!")
			return
					
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
			#create a transform, parent this transform to target parents
			#create the connexions
			#parent targets to hook transform
			parent = mc.listRelatives(hooked_list[i], parent=True)
			hook_transform = mc.createNode("transform", n="hook_%s_for_%s"%(hooker_list[i], hooked_list[i]), parent=parent[0]) 
			mc.connectAttr('%s.worldMatrix'%hooker_list[i], "%s.offsetParentMatrix"%hook_transform)
			mc.parent(hooked_list[i], hook_transform)
			
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
			if (command == "neck_head"):
				ctrl_name = obj.replace("loc_", "")
			if (command == "clavicule_controller"):
				ctrl_name = obj.replace("loc_", "")
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
					created_curve = self.import_curve_function("event", "controller_creation")
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
		if (command == "spline_fk") or (command == "spline_ik") or (command == "spline_fk_ik") or (command == "neck_head"):	
			#creation of the target for the hips and the shoulders at the end of their hierarchy
			"""
			FK HIERARCHY 
				parent the target transform (hips / shoulders) to the first / last controller's curve (FK CONTROLLER)
			IK / FK HIERARCHY
				parent the target transform (hips / shoulders) to the first / last controller's curve (IK CONTROLLER)

			create a setting button to define to which elements thoses target transform should be hooked!
			"""

			return created_controller, root_list
		else:
			return created_controller

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

	def get_transform(self, shape):
		return mc.listRelatives(shape, parent=True, path=True)[0]

	def get_sn(self, obj):
		return obj.split("|")[-1].split(":")[-1]
							


Application()
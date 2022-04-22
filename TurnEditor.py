import maya.cmds as mc
import pymel.core as pm 
import pickle

from functools import partial






class Application:
	def __init__(self):
		self.window_width=310
		self.pedestal_mesh = None

		#call the main interface
		self.main_interface()



	"""
	program which allow user to create Turn set
		Depending of the scene:
			if selection:
				all selection in a group
			if not selection:
				all outliner in a group
		Define a mesh as pedestal?
		(mesh in the project/ scene)
			-> in the project? import it

			-> center the pedestal, center the group to turn

		Depending of the bounding box of the transform
			-> Center the pivot
			-> Create a light set 
				(number of light)
				(Distance by factor (lateral, vertical))

		Mesh rotation
			x1 -> y1 angle between t1 and t2
		Light rotation
			x2 -> y2 angle between t3 and t4
		Camera rotation
			x3 -> y3 angle between t5 and t6
	"""

	def main_interface(self):
		self.window = mc.window(sizeable=False)
		mc.columnLayout(adjustableColumn=True)

		mc.frameLayout(label="Turn Editor Tool", collapsable=True, collapse=False, width=self.window_width, backgroundColor=(0.138, 0.102, 0.224))

		#pedestal selection
		self.pedestal_enable_ui = mc.checkBox(label="Define a pedestal",value=False, changeCommand=self.enable_pedestal_function)
		self.pedestal_in_scene_ui = mc.checkBox(label="Pedestal in the scene", value=True, enable=False, changeCommand=self.enable_pedestal_button_function)
		self.pedestal_button_ui = mc.button(label="Pedestal on computer", enable=False, command=self.define_pedestal_mesh_function)

		mc.separator( height=10, style='singleDash' )
		#lights settings
		mc.text(label="Light number")
		self.light_number_ui = mc.intField(minValue=1)
		mc.separator( height=20, style='singleDash' )

		#rotation settings
		#creation of a tab layout
		"""
			item settings
			light settings
			camera settings
		"""
		self.turn_form = mc.formLayout()
		self.turn_tabs = mc.tabLayout(innerMarginWidth=50, innerMarginHeight=0)
		mc.formLayout( self.turn_form, edit=True, attachForm=((self.turn_tabs, 'top', 0), (self.turn_tabs, 'left', 0), (self.turn_tabs, 'bottom', 0), (self.turn_tabs, 'right', 0)))

		#ITEM TAB
		self.item_tab = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width/2), (2, self.window_width/2)))
		mc.text(label="Start angle")
		self.item_start_angle = mc.intField(value=0)
		mc.text(label="End angle")
		self.item_end_angle = mc.intField(value=90)
		mc.text(label="Start frame")
		self.item_start_frame = mc.intField(value=1, minValue=1)
		mc.text(label="End frame")
		self.item_end_frame = mc.intField(value=10, minValue=1)
		mc.setParent("..")

		#LIGHT TAB
		self.light_tab = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width/2), (2, self.window_width/2)))
		mc.text(label="Number of lights")
		self.light_number = mc.intField(value=0)
		mc.text(label="Start angle")
		self.item_start_angle = mc.intField(value=0)
		mc.text(label="End angle")
		self.item_end_angle = mc.intField(value=90)
		mc.text(label="Start frame")
		self.item_start_frame = mc.intField(value=1, minValue=1)
		mc.text(label="End frame")
		self.item_end_frame = mc.intField(value=10, minValue=1)
		mc.setParent("..")



		mc.tabLayout(self.turn_tabs, edit=True, tabLabel=((self.item_tab, "Items settings"), (self.light_tab, "Lights settings")))
		


		



		mc.setParent("..")


		mc.setParent("..")
		mc.setParent("..")

		mc.showWindow()



	def enable_pedestal_function(self, event):
		checkbox = mc.checkBox(self.pedestal_enable_ui, query=True, value=True)
		in_scene = mc.checkBox(self.pedestal_in_scene_ui, query=True, value=True)

		mc.checkBox(self.pedestal_in_scene_ui, edit=True, enable=checkbox)
		if (checkbox ==True) and (in_scene == False):
			mc.button(self.pedestal_button_ui, edit=True, enable=True)
		else:
			mc.button(self.pedestal_button_ui, edit=True, enable=False)
		

	def enable_pedestal_button_function(self, event):
		checkbox = mc.checkBox(self.pedestal_in_scene_ui, query=True, value=True)
		if checkbox == True:
			checkbox = False
		else:
			checkbox = True
		mc.button(self.pedestal_button_ui, edit=True, enable=checkbox)


	def define_pedestal_mesh_function(self, event):
		self.pedestal_file = mc.fileDialog2(dialogStyle=2, fm=1, ff="(*.obj *.ma *.mb)")
		if self.pedestal_file == None:
			mc.warning("No file selected!")
			return



Application()
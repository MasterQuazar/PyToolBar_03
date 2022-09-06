import maya.cmds as mc





class Application:
	def __init__(self):
		print("hello world!")
		self.main_interface()




	def main_interface(self):



		self.main_window = mc.window(sizeable=True, height=310, width=310)


		mc.columnLayout(adjustableColumn=True)


		
		self.test2 = mc.button(label="test")
		self.test1 = mc.button(label="delete", command=self.test_function)

		mc.showWindow()



	def test_function(self, event):
		mc.deleteUI(self.test2, control=True)



Application()






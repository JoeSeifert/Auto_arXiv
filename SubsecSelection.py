from tkinter import *
from tkinter import ttk


class SubsecSelection:

	def __init__(self,root):
		self.subsec_list = []
		self.root = root
		self.mainframe = ttk.Frame(self.root)
		self.all_subsecs_shorthand = ('cond-mat.dis-nn', 'cond-mat.mtrl-sci', 'cond-mat.mes-hall', 'cond-mat.other', 'cond-mat.quant-gas', 
			'cond-mat.soft', 'cond-mat.stat-mech', 'cond-mat.str-el', 'cond-mat.supr-con')
		self.all_subsecs_formal = ('Disordered Systems and Neural Networks', 'Materials Science', 'Mesoscale and Nanoscale Physics', 'Other Condensed Matter', 'Quantum Gases', 
			'Soft Condensed Matter', 'Statistical Mechanics', 'Strongly Correlated Electrons', 'Superconductivity')

		self.checkbutton_variable_list = []
		self.checkbutton_list = []
		for i in range(len(self.all_subsecs_formal)):
			self.checkbutton_variable_list.append(BooleanVar())
			self.checkbutton_list.append(ttk.Checkbutton(self.mainframe, variable=self.checkbutton_variable_list[i], text=self.all_subsecs_formal[i]))
			self.checkbutton_list[i].grid(row=i, column=0)
		Button(self.mainframe, text='SUBMIT', command=self.submit_subsecs).grid(row=len(self.all_subsecs_formal), column=0)
		self.mainframe.grid(row=0, column=0)
		self.root.bind_all('<Return>', self.submit_subsecs)


	def submit_subsecs(self, *args):
		ind_list = []
		for i,selection in enumerate(self.checkbutton_variable_list):
			if selection.get():
				self.subsec_list.append(self.all_subsecs_shorthand[i])

		# print('Selected Subsections: {}'.format(', '.join(self.subsec_list)))
		self.root.destroy()
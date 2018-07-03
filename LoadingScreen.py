from tkinter import *
from tkinter import ttk
import autoArxiv as aa 

class LoadingScreen:

	def __init__(self,root,subsec):
		self.entry_list = []
		self.root = root
		self.subsec_list = subsec
		self.subsec_count = len(self.subsec_list)
		# self.total_progress = 0
		self.progress_step = 100 / self.subsec_count - 0.01
		# self.pbar_variable = DoubleVar()
		# self.pbar_variable.set(0.0)

		Label(self.root, text='Loading...', font='Helvetica 12 bold').grid(row=0, column=0, padx=20, pady=20)
		self.progress_bar = ttk.Progressbar(self.root, mode='determinate')
		self.progress_bar.grid(row=1, column=0, sticky='news')
		self.root.after(50, self.gather_articles)

	def pbar_step(self):
		self.progress_bar.step(self.progress_step)
		self.progress_bar.update()

	def gather_articles(self):
		# call API for recent articles, parse through them, give resulting articles as entries
		for subsec in self.subsec_list:
			print('Acquiring articles for {}'.format(subsec))
			response = aa.callAPI(subsec)
			entries = aa.parseAPIResponse(response, printPrompt=False)
			entries = entries[1:len(entries)] # parsing entries catches some metadata at the beginning. This removes it.

			# Patchwork author list fix because it looked super duper ugly
			for i,entry in enumerate(entries):
				auth_list = []
				try:
					if type(entry['author']) is str:			# for when author list is only one entry
						entry['author'] = [entry['author']] 
					for author in entry['author']:
						author = author.split('<name>')[1]
						author = author.split('</name>')[0]
						auth_list.append(author)
					entry['author'] = auth_list
					entries[i] = entry
				except KeyError:
					continue
			for entry in entries:
				entry['subsection'] = subsec
				self.entry_list.append(entry)
			self.pbar_step()
			# self.total_progress += self.progress_step
			# self.pbar_variable.set(self.total_progress)
		self.root.destroy()
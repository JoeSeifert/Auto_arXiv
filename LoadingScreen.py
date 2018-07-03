from tkinter import *
from tkinter import ttk
import autoArxiv as aa

class LoadingScreen:

	def __init__(self,root,subsec):
		self.entry_list = []
		self.root = root
		self.subsec = subsec
		Label(self.root, text='Loading...', font='Helvetica 12 bold').grid(row=0, column=0, padx=20, pady=20)
		self.root.after(50, self.gather_articles)

	def gather_articles(self):
		# call API for recent articles, parse through them, give resulting articles as entries
		response = aa.callAPI(self.subsec)
		entries = aa.parseAPIResponse(response)
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
		self.entry_list = entries
		self.root.destroy()
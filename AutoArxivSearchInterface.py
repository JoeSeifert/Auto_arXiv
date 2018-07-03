from tkinter import *
from tkinter import ttk
import articleReader as ar 
import autoArxiv as aa
import time
from PIL import Image, ImageTk

# To do:
# - Comment everything, you lazy fuck
# - Make the settings actually do something
# ---- number of recent articles gathered. Right now it's 500
# ---- maybe in the future: legacy vs. current article reader
# - Find a way to make the command line not open when the program starts -- py2exe
# - add key-bindings for ease of use
# ---- display new articles when query is double clicked
# ---- bind enter to submit on build_query window
# - Future changes for increased speed:
# ---- change how feed is parsed, I think current method of looping through every character may be a bit slow
# ---- store the old feed in a file, only parse up to the latest entry
# ---- re-add searches for specific queries, so the list when printing all articles goes further back than just ~1 month without taking forever
# - Make sure user can't break the build query function
# ----make build query function look nicer!
# - Fix articleReader issues (LaTeX)
# - 256-bit encrypt slog files for added security
# - backup slog files? Just title with the date and store in another folder

# Kinda tough problem:
# - I want my program elemnts to be 'black boxes'. Standard input, standard output, if I need to change something I can just "lift the hood" and change it and it doesn't change anything else
# - With the article reader, this is true. You give it a root to appear in (a top level, for example) and an entry list, and it will open the article-reader and read off the articles.
# - I want to be able to update/adjust settings through the arxivReader. This means I need to input settings, be able to change in them in the articleReader, and output them back. 
# - How do I do this with a class? Maybe add a function wrapper to calling the article reader that handles the settings? I would still need a checkbox on the article-reader though. Cannot be completely independent


# Some thoughts
# - it would look super slick if the info box went back to the welcome message after a few seconds of an error being displayed :P
# - standardize top levels (aside from article reader)? Call them all self.tl, destroy after use?

# Changes:
# 2018-07-03 -- removed settings button for now. Code is still there to use it in the future, but it seemed pointless for now


class SearchInterface:

	def __init__(self, root, entries):
		self.filename = 'slog.txt'
		self.slog = aa.FullSearchLog(self.filename)
		self.settings = ProgramSettings('settings.txt')
		self.all_articles=entries
		self.root = root
		self.root.title('ArXiv Manager by Joe')
		self.current_article_list = []
		self.current_query = StringVar()

		# Set up frames
		self.mainframe = ttk.Frame(self.root)
		self.query_select_frame = ttk.Frame(self.mainframe, borderwidth= 2, relief='sunken', width=200, height=250)
		self.option_select_frame = ttk.Frame(self.mainframe, borderwidth= 2, relief='sunken', width=200, height=150)
		self.infobox_frame = ttk.Frame(self.mainframe, borderwidth= 2, relief='sunken', width=200, height=100)

		# setup column and row sizes to fit in frames
		self.query_select_frame.rowconfigure(0, minsize=20)
		self.query_select_frame.rowconfigure(1, minsize=210)
		self.query_select_frame.rowconfigure(2, minsize=20)
		self.query_select_frame.columnconfigure(0, minsize=200)
		for i in range(3):
			self.option_select_frame.rowconfigure(i, minsize=50)
		for i in range(2):
			self.option_select_frame.columnconfigure(i, minsize=100)
		self.infobox_frame.rowconfigure(0, minsize=100)
		self.infobox_frame.columnconfigure(0, minsize=200)

		# list of variables for search box
		self.search_list=()
		for key,_ in self.slog.sdict.items():
			self.search_list += (key,)
		self.lbox_variable = StringVar(value= self.search_list)
		self.current_query.set('')

		# setting up query selection
		Label(self.query_select_frame, text='Select a query: ').grid(row=0, column=0, sticky=W)
		self.query_selection = Listbox(self.query_select_frame, listvariable= self.lbox_variable)
		self.query_selection.bind('<<ListboxSelect>>', self.set_query_label)
		self.query_selection.bind('<Double-Button-1>', self.read_new_articles)
		self.query_selection.grid(row=1, column=0, sticky=(N,E,W,S))
		self.all_queries = BooleanVar()
		self.all_queries_button = ttk.Checkbutton(self.query_select_frame, variable=self.all_queries, command=self.all_queries_selected, text='Select all queries')
		self.all_queries_button.grid(row=2, column=0, sticky=W)
		# self.original_gear = Image.open('gear.gif')
		# resized = self.original_gear.resize((20,20), Image.ANTIALIAS)
		# self.gear_pic = ImageTk.PhotoImage(resized)
		# self.settings_button = Button(self.query_select_frame, image=self.gear_pic, command=self.settings_window)
		# self.settings_button.grid(row=2, column=0, sticky=E)

		# setting up options
		self.button1 = Button(self.option_select_frame, text= 'New Articles', command=self.read_new_articles)
		self.button1.grid(row=0,column=0)
		self.button2 = Button(self.option_select_frame, text= 'All articles', command=self.read_all_articles)
		self.button2.grid(row=0, column=1)
		self.button3 = Button(self.option_select_frame, text= 'Query Info', command=self.print_query_info)
		self.button3.grid(row=1,column=0)
		self.button4 = Button(self.option_select_frame, text= 'New Query', command=self.build_new_query_window)
		self.button4.grid(row=1,column=1)
		self.button5 = Button(self.option_select_frame, text= 'Delete Query', command=self.delete_query_confirmation_window)
		self.button5.grid(row=2, column=0)
		self.button6 = Button(self.option_select_frame, text= 'Edit Query', command=lambda: self.build_new_query_window(mode='edit'))
		self.button6.grid(row=2, column=1)

		# setting up info box
		self.status_msg = StringVar(value='Welcome to Auto-arXiv')
		self.status = Label(self.infobox_frame, textvariable=self.status_msg, font=('Helvetica', 10, 'bold'), wraplength= 170)
		self.status.grid(row=0, column=0, sticky=(N,S,E,W))

		# frame grids
		self.mainframe.grid(row=0, column=0)
		self.query_select_frame.grid(row=0, column=0, columnspan=2, rowspan=5)
		self.option_select_frame.grid(row=2, column=2, columnspan=2, rowspan=3)
		self.infobox_frame.grid(row=0, column=2, columnspan=2, rowspan=2)

	def set_query_label(self, *args):
		if self.all_queries.get():
			return
		selection = self.query_selection.curselection()
		self.current_query.set(self.search_list[selection[0]])

	def read_new_articles(self, *args):

		# a couple potential bugs:
		# - if a topic isn't posted about for a loooooong time (>1 month), then highestID will be 0. This will cause the log to be written as thus, making any article it sees the "newest article". Perhaps no negative consequences?

		self.current_article_list=[]
		if self.all_queries.get():
			query_list = self.search_list
			self.status_msg.set('Reading new articles for all queries')
		elif self.current_query.get() == '':
			self.status_msg.set('Please select a query!')
			return
		else:
			query_list = [self.current_query.get()]
			self.status_msg.set('Reading new articles for {}'.format(self.current_query.get()))

		for query_label in query_list:
			search = self.slog.sdict[query_label]
			temp_article_list = aa.searchAllWords(self.all_articles,search['queries'])

			# From articles that match the search, lists all articles posted between today and the last time checked (even if run multiple times)
			if search['dateLastChecked'] == aa.today():
				temp_article_list = aa.searchNewArticles(temp_article_list,search['secondLastIDSeen'])
			else:
				temp_article_list = aa.searchNewArticles(temp_article_list,search['lastIDSeen'])

			# find newest ID, update log accordingly
			if len(temp_article_list) != 0:
				highestID = aa.findNewestID(temp_article_list)
				if search['lastIDSeen'] != highestID:
					self.slog.updateLog(query_label,aa.today(),highestID,search['lastIDSeen'])
				else:
					self.slog.updateLog(query_label,search['dateLastChecked'],search['lastIDSeen'],search['secondLastIDSeen'])
			self.current_article_list += temp_article_list

		self.current_article_list = aa.sortEntriesByDate(self.current_article_list)

		# article reader
		if len(self.current_article_list) != 0:
			article_top_level = Toplevel(self.root)
			article_reader = ar.ArXivGui(article_top_level,self.current_article_list)
		else:
			if self.all_queries.get():
				self.status_msg.set('No new articles to present!')
			else:
				self.status_msg.set('No new articles to present for {}!'.format(self.current_query.get()))
			# print in info box: No new articles to present! (Make this red text so it's obvious?)

	def read_all_articles(self, *args):

		self.current_article_list=[]
		if self.all_queries.get():
			query_list = self.search_list
			self.status_msg.set('Reading all articles for all queries')
		elif self.current_query.get() == '':
			self.status_msg.set('Please select a query!')
			return
		else:
			query_list = [self.current_query.get()]
			self.status_msg.set('Reading all articles for {}'.format(self.current_query.get()))

		for query_label in query_list:
			search = self.slog.sdict[query_label]
			temp_article_list = aa.searchAllWords(self.all_articles,search['queries'])

		# find newest ID, update log accordingly
			if len(temp_article_list) != 0:
				highestID = aa.findNewestID(temp_article_list)
				if search['lastIDSeen'] != highestID:
					self.slog.updateLog(query_label,aa.today(),highestID,search['lastIDSeen'])
				else:
					self.slog.updateLog(query_label,search['dateLastChecked'],search['lastIDSeen'],search['secondLastIDSeen'])
			self.current_article_list += temp_article_list

		self.current_article_list = aa.sortEntriesByDate(self.current_article_list)

		# article reader
		if len(self.current_article_list) != 0:
			article_top_level = Toplevel(self.root)
			article_reader = ar.ArXivGui(article_top_level,self.current_article_list)
		else:
			self.status_msg.set('No articles to present!')
			# (Make this red text so it's obvious?)

	def print_query_info(self):

		if self.current_query.get() == '':
			self.status_msg.set('Please select a query!')
			return

		self.status_msg.set('Printing info for {}'.format(self.current_query.get()))
		search = self.slog.sdict[self.current_query.get()]
		print_info_top_level = Toplevel(self.root)
		info_frame = ttk.Frame(print_info_top_level, borderwidth=2, relief='sunken', width=100, height=100)

		query_label = StringVar(value='Label: '+self.current_query.get())
		queries = StringVar(value='Queries: '+str(search['queries']))
		date_last_checked = StringVar(value='Date last article seen: '+search['dateLastChecked'])
		last_ID_seen = StringVar(value='Last ID seen: '+str(search['lastIDSeen']))
		second_Last_ID_Seen = StringVar(value='Second last ID seen: '+str(search['secondLastIDSeen']))
		info_frame.grid(row=0, column=0)
		Label(info_frame, textvariable=query_label).grid(row=0, column=0)
		Label(info_frame, textvariable=queries).grid(row=1, column=0)
		Label(info_frame, textvariable=date_last_checked).grid(row=2, column=0)
		Label(info_frame, textvariable=last_ID_seen).grid(row=3, column=0)
		Label(info_frame, textvariable=second_Last_ID_Seen).grid(row=4, column=0)

	def build_new_query_window(self, mode='build'):
		# queries are separated by commas in the input
		if mode=='build':
			self.status_msg.set('Building new query')
		elif mode=='edit':
			if self.current_query.get() == '':
				self.status_msg.set('Please select a query!')
				return
			self.status_msg.set('Editing {} query'.format(self.current_query.get()))

		self.query_builder_top_level = Toplevel(self.root)
		qb_frame = ttk.Frame(self.query_builder_top_level, borderwidth=2, relief='sunken', width=100, height=100)

		self.qlabel_text = StringVar()
		self.queries_text = StringVar()
		if mode=='edit':
			self.qlabel_text.set(self.current_query.get())
			self.queries_text.set(separate_by_commas(self.slog.sdict[self.current_query.get()]['queries']))

		qlabel = Entry(qb_frame, textvariable=self.qlabel_text)
		search_queries = Entry(qb_frame, textvariable= self.queries_text)
		qlabel.focus_set()

		Label(qb_frame, text= 'Query label').grid(row=0, column=0, sticky=W)
		Label(qb_frame, text= 'All search queries, separated by commas: ').grid(row=1, column=0, sticky=W)
		Button(qb_frame, text= 'Submit', command=lambda: self.build_new_query_button(mode)).grid(row=2, column=0, columnspan=2)
		self.query_builder_top_level.bind('<Return>', lambda event, mode_ = mode: self.build_new_query_button(mode_))

		qb_frame.grid(row=0, column=0)
		qlabel.grid(row=0, column=1)
		search_queries.grid(row=1, column=1)

	def build_new_query_button(self, mode):
		label = self.qlabel_text.get()
		if mode=='build' and label in self.slog.sdict.keys():
			self.status_msg.set('Label already exists, choose another label!')
			return 
		elif mode=='edit' and label in [x for x in self.slog.sdict.keys() if x != self.current_query.get()]:
			self.status_msg.set('Label already exists, choose another label!')
			return
		search_queries_text = self.queries_text.get()
		search_queries_text = search_queries_text.split(',')
		for ind in range(len(search_queries_text)):
			while search_queries_text[ind].startswith(' '):
				search_queries_text[ind] = search_queries_text[ind][1:]
			while search_queries_text[ind].endswith(' '):
				search_queries_text[ind] = search_queries_text[ind][:-1]

		final_query_list = []
		for query in search_queries_text:
			query = query.lower()
			if query not in final_query_list:
				final_query_list.append(query)
				if aa.isChemicalCompound(query):
					final_query_list.append(aa.buildLatexEquiv(query))
		if mode=='build':
			self.slog.createFullSearch(label, final_query_list, aa.today(), 1, 1)
		elif mode=='edit':
			self.slog.editQueryInLog(self.current_query.get(),label,final_query_list)

		# re-update the query list!
		self.search_list=()
		for key,_ in self.slog.sdict.items():
			self.search_list += (key,)
		self.lbox_variable.set(self.search_list)
		self.current_query.set(self.search_list[0])

		if mode=='build':
			self.status_msg.set('{} was created'.format(label))
		elif mode=='edit':
			self.status_msg.set('{} was edited'.format(label))
		self.current_query.set(label)

		self.query_builder_top_level.destroy()

	def delete_query_confirmation_window(self):
		# asks if user is suuuper sure

		if self.current_query.get() == '':
			self.status_msg.set('Please select a query!')
			return

		if self.all_queries.get():
			return
		self.tl = Toplevel(self.root)
		dq_frame = ttk.Frame(self.tl, borderwidth=2, relief='sunken', width=100, height=100)

		for i in range(2):
			dq_frame.rowconfigure(i, minsize=50)
			dq_frame.columnconfigure(i, minsize=50)

		Label(dq_frame, text="Are you sure you want to delete {} query?".format(self.current_query.get()), justify = CENTER).grid(row=0, column=0, columnspan=2)
		Button(dq_frame, text="Yes", command=self.delete_query_yes).grid(row=1, column=0)
		Button(dq_frame, text="No", command=lambda: self.tl.destroy()).grid(row=1, column=1)

		dq_frame.grid(row=0, column=0)

	def delete_query_yes(self):
		self.status_msg.set('Query {} was deleted'.format(self.current_query.get()))
		self.slog.deleteFromLog(self.current_query.get())
		# re-update the query list!
		self.search_list=()
		for key,_ in self.slog.sdict.items():
			self.search_list += (key,)
		self.lbox_variable.set(self.search_list)
		try:
			self.current_query.set(self.search_list[0])
		except IndexError:
			self.current_query.set('')
		self.tl.destroy()

	def all_queries_selected(self):
		if self.all_queries.get():
			self.query_selection.config(state= DISABLED)
		else:
			self.query_selection.config(state= NORMAL)

	def settings_window(self):
		self.status_msg.set('Altering program settings')
		self.tl = Toplevel(self.root)
		self.settings_frame = ttk.Frame(self.tl, borderwidth=2, relief='sunken', width=100, height=100)
		self.max_list_length = StringVar()
		self.max_list_length.set(self.settings.settings['max_list_length'])
		self.collapse_abstract = BooleanVar()
		self.collapse_abstract.set(self.settings.settings['collapse_abstract']=='True')

		Label(self.settings_frame, text='Maximum length of article list (default = 100): ').grid(row=0, column=0, sticky=W, padx=20, pady=20)
		self.max_list_length_entry = Entry(self.settings_frame, textvariable=self.max_list_length)
		self.max_list_length_entry.grid(row=0, column=1, padx=20, pady=20)

		self.collapse_abstract_button = ttk.Checkbutton(self.settings_frame, variable=self.collapse_abstract, text="Collapse Abstracts?")
		self.collapse_abstract_button.grid(row=1, column=0, columnspan=2, sticky=W, padx=20, pady=20)

		self.submit_button = Button(self.settings_frame, text='Submit', command=self.settings_submit)
		self.submit_button.grid(row=2, column=0, columnspan=2, padx=20, pady=20)

		self.settings_frame.grid(row=0, column=0)

	def settings_submit(self):
		self.settings.change_setting('max_list_length', self.max_list_length.get())
		print('Max List Length is now {}'.format(self.settings.settings['max_list_length']))
		self.settings.change_setting('collapse_abstract', str(self.collapse_abstract.get()))
		print('Collapse Abstract is now set to {}'.format(self.settings.settings['collapse_abstract']))
		self.tl.destroy()

class ProgramSettings:

	def __init__(self, filename):
		self.filename = filename
		self.settings = {}
		self.read_settings_log()

	def make_settings_file(self):
		f = open(self.filename, 'w+')
		f.write('max_list_length=100\n')
		f.write('collapse_abstract=True\n')
		f.close()

	def read_settings_log(self):
		try:
			f = open(self.filename, 'r')
		except FileNotFoundError:
			self.make_settings_file()
			f = open(self.filename, 'r')
		for line in f.readlines():
			line = line.replace('\n','').split('=')
			self.settings[line[0]] = line[1]
		f.close()
	
	def write_log(self):
		self.clear_log_contents()
		f = open(self.filename, 'w')
		for key, value in self.settings.items():
			f.write('{0}={1}\n'.format(key,value))
		f.close()

	def clear_log_contents(self):
		f = open(self.filename,'r+')
		f.truncate()
		f.close()

	def change_setting(self,setting_key,new_value):
		self.settings[setting_key] = str(new_value)
		self.write_log()

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


	def submit_subsecs(self):
		ind_list = []
		for i,selection in enumerate(self.checkbutton_variable_list):
			if selection.get():
				self.subsec_list.append(self.all_subsecs_shorthand[i])

		# print('Selected Subsections: {}'.format(', '.join(self.subsec_list)))
		self.root.destroy()

class LoadingScreen:

	def __init__(self,root,subsec):
		self.entry_list = []
		self.root = root
		self.subsec_list = subsec
		Label(self.root, text='Loading...', font='Helvetica 12 bold').grid(row=0, column=0, padx=20, pady=20)
		self.root.after(50, self.gather_articles)

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
		self.root.destroy()

# helper functions below

def separate_by_commas(qlist):
	final = ''
	for q in qlist:
		 final += q + ', '
	return final[:-2]

def main():
	select_subsec = Tk()
	y = SubsecSelection(select_subsec)
	select_subsec.mainloop()
	subsec_list = y.subsec_list

	loading_screen = Tk()
	x = LoadingScreen(loading_screen, subsec_list)
	loading_screen.mainloop()
	entry_list = x.entry_list

	root = Tk()
	gui = SearchInterface(root, entry_list)
	root.mainloop()

def test():
	root = Tk()
	x = SubsecSelection(root)
	root.mainloop()

if __name__ == '__main__':
	main()
import autoArxiv as aa 
from tkinter import *
from tkinter import ttk
import webbrowser as wb 

# Looks good so far!
# To Do:
# - Make Latex things look pretty.
# ---- I made a function to remove Latex formatting, but it keeps Latex functions like \frac and \mathbb and stuff like that. Also greek characters like \nu would just be 'nu'
# ---- I bet it's possible to find out what command is after the slash just by finding what's between the \ and the next non-alpha-numeric character. Then keep the greek letters (which can probably be displayed using some encoding?) and toss the others
# ---- Other option is to compile title and summary in Latex, save as a PDF/PNG, have article reader display the PDF/PNG instead of the text.

def gather_articles(subsec):
		# call API for recent articles, parse through them, give resulting articles as entries
		response = aa.callAPI(subsec)
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
		return entries

def format_date(date):
	datelist = date.split('T')[0].split('-')
	return '{0}/{1}/{2}'.format(datelist[1],datelist[2],datelist[0])

class ArXivGui:

	def __init__(self,root,entry_list):
		self.root = root
		self.entries = entry_list
		self.article_index = 0 
		self.current_entry = self.entries[self.article_index]
		self.article_list_len = len(self.entries)

		# Construct frames:
		self.mainframe = ttk.Frame(root)
		self.artlist_frame = ttk.Frame(self.mainframe, borderwidth=2, relief='sunken', width=500, height=500)
		self.article_frame = ttk.Frame(self.mainframe, borderwidth=2, relief='flat', width=500, height=500)
		self.title_frame = ttk.Frame(self.article_frame, width=500, height=60)
		self.author_frame = ttk.Frame(self.article_frame,width=500, height=50)
		self.abstract_frame = ttk.Frame(self.article_frame, width=500, height=360)
		self.dateid_frame = ttk.Frame(self.article_frame, width=500, height=30)

		# canvas stuff separate because I'm new 
		self.artlist = Canvas(self.artlist_frame, width=500, height=500)
		self.artlist.config(scrollregion=(0,0,500, self.article_list_len*100))
		self.scrollbar = Scrollbar(self.artlist_frame, command=self.artlist.yview)
		self.artlist.config(yscrollcommand=self.scrollbar.set)
		self.root.bind_all("<MouseWheel>", self.on_mousewheel)
		self.root.bind_all("<Up>", self.on_upkey)
		self.root.bind_all("<Down>", self.on_downkey)

		# set up article list, all frames are located in self.art_frame_list
		self.art_frame_list = []
		for i in range(self.article_list_len):
			self.art_frame_list.append(ttk.Frame(self.artlist, width=500, height=100, borderwidth=2, relief='sunken'))
			self.art_frame_list[i].rowconfigure(0, minsize=50)
			self.art_frame_list[i].columnconfigure(0, minsize=125)
			self.art_frame_list[i].rowconfigure(1, minsize=50)
			self.art_frame_list[i].columnconfigure(1, minsize=250)
			self.art_frame_list[i].columnconfigure(2, minsize=125)
			self.art_frame_list[i].article_number = i
			self.artlist.create_window(250, 100*i+50, window=self.art_frame_list[i])
			self.art_frame_list[i].bind('<Button-1>', self.on_leftclick)
			self.art_frame_list[i].title = Label(self.art_frame_list[i], text=self.entries[i]['title'].replace('\n', ''), font=('Helvetica', 12, 'bold'), wraplength=500, justify='left')
			self.art_frame_list[i].authors = Label(self.art_frame_list[i], text=self.construct_author_list(self.entries[i]), wraplength=375, justify='left')
			self.art_frame_list[i].title.grid(row=0, column=0, columnspan=3, sticky=W)
			self.art_frame_list[i].authors.grid(row=1, column=1, columnspan=2, sticky=W)
			self.art_frame_list[i].title.bind('<Button-1>', self.on_leftclick)
			self.art_frame_list[i].authors.bind('<Button-1>', self.on_leftclick)

		# styles for highlighed objects, highlight first article
		self.highlighted_frame = ttk.Style()
		self.highlighted_frame.configure('highlight.TFrame', background='SkyBlue1')
		self.unhighlighted_frame = ttk.Style()
		self.unhighlighted_frame.configure('unhighlight.TFrame', background='SystemButtonFace')

		self.highlighted_widget = self.art_frame_list[0]
		self.highlighted_widget.configure(style='highlight.TFrame')
		self.highlighted_widget.title.configure(bg='SkyBlue1')
		self.highlighted_widget.authors.configure(bg='SkyBlue1')

		# configure row/columns, do this manually so I know exactly what I get
		self.title_frame.columnconfigure(0,minsize=500)
		self.title_frame.rowconfigure(0,minsize=60)
		self.author_frame.columnconfigure(0,minsize=500)
		self.author_frame.rowconfigure(0,minsize=50)
		self.abstract_frame.columnconfigure(0,minsize=500)
		self.abstract_frame.rowconfigure(0,minsize=360)
		self.dateid_frame.columnconfigure(0,minsize=166.66)
		self.dateid_frame.rowconfigure(0,minsize=30)
		self.dateid_frame.columnconfigure(1,minsize=166.66)
		self.dateid_frame.columnconfigure(2,minsize=166.66)

		self.artlist_frame.rowconfigure(0, minsize=500)
		self.artlist_frame.columnconfigure(0, minsize=490)
		self.artlist_frame.columnconfigure(1, minsize=10)

		# selected article display
		self.title_text = StringVar()
		self.title_text.set(self.current_entry['title'].replace('\n',''))
		self.title = Label(self.title_frame, textvariable= self.title_text, font=('Helvetica', 12, 'bold'),wraplength=500).grid(row=0, column=0)

		self.author_text = StringVar()
		self.author_text.set(self.construct_author_list(self.current_entry))
		self.author = Label(self.author_frame, textvariable= self.author_text, wraplength=500).grid(row=0, column=0)

		self.abstract_text = StringVar()
		self.abstract_text.set(self.current_entry['summary'].replace('\n',' '))
		self.abstract = Label(self.abstract_frame, textvariable= self.abstract_text, wraplength=500).grid(row=0, column=0)

		self.id_text = StringVar()
		self.id_text.set(self.current_entry['id'])
		self.id = Label(self.dateid_frame, textvariable= self.id_text, fg='blue', font= "TkDefaultFont 10 underline")
		self.id.grid(row=0, column=1)
		self.id.bind('<Button-1>', self.click_on_arxiv_link)

		self.date_text = StringVar()
		self.date_text.set(format_date(self.current_entry['published']))
		self.date = Label(self.dateid_frame, textvariable= self.date_text).grid(row=0, column=0)

		self.subsec_text = StringVar()
		self.subsec_text.set(self.current_entry['subsection'])
		self.subsec_label = Label(self.dateid_frame, textvariable= self.subsec_text).grid(row=0, column=2)

		# placing everything
		self.mainframe.grid(row=0, column=0)
		self.artlist_frame.grid(row=0, column=0)
		self.article_frame.grid(row=0, column=1)
		self.title_frame.grid(row=0, column=0)
		self.author_frame.grid(row=1, column=0)
		self.abstract_frame.grid(row=2, column=0)
		self.dateid_frame.grid(row=3, column=0)
		self.artlist.grid(row=0, column=0)
		self.scrollbar.grid(row=0, column=1, sticky=(N,S))

	def change_article(self):
		self.title_text.set(self.current_entry['title'].replace('\n', ''))
		self.author_text.set(self.construct_author_list(self.current_entry))
		self.abstract_text.set(self.current_entry['summary'].replace('\n', ' '))
		self.id_text.set(self.current_entry['id'])
		self.date_text.set(format_date(self.current_entry['published']))
		self.subsec_text.set(self.current_entry['subsection'])

	def construct_author_list(self, entry):
		final_string = ''
		for author in entry['author']:
			final_string = final_string + author + ', '
		return final_string[0:len(final_string)-2]

	def click_on_arxiv_link(self, *args):
		wb.open_new(self.current_entry['id'])	

	def on_mousewheel(self, event):
		self.artlist.yview_scroll(-int(event.delta/120), "units")

	def on_downkey(self, event):
		if self.article_index < (self.article_list_len - 1):
			self.article_index+= 1
			self.current_entry = self.entries[self.article_index]
			self.change_article()
			self.highlight_current_entry(self.art_frame_list[self.article_index])

	def on_upkey(self, event):
		if self.article_index > 0:
			self.article_index-= 1
			self.current_entry = self.entries[self.article_index]
			self.change_article()
			self.highlight_current_entry(self.art_frame_list[self.article_index])			

	def on_leftclick(self, event):
		# if either label in the frame is clicked, AttributeError is raised and the encapsualting frame is selected instead
		try:
			self.current_entry = self.entries[event.widget.article_number]
			self.article_index = event.widget.article_number
			self.highlight_current_entry(event.widget)
		except AttributeError:
			self.current_entry = self.entries[event.widget.master.article_number]
			self.article_index = event.widget.master.article_number
			self.highlight_current_entry(event.widget.master)
		self.change_article()

	def highlight_current_entry(self, widget):
		# entry widget should be the frame containing the title and authors
		self.highlighted_widget.configure(style='unhighlight.TFrame')
		self.highlighted_widget.title.configure(bg='SystemButtonFace')
		self.highlighted_widget.authors.configure(bg='SystemButtonFace')

		self.highlighted_widget = widget
		widget.configure(style='highlight.TFrame')
		widget.title.configure(bg='SkyBlue1')
		widget.authors.configure(bg='SkyBlue1')

def main():
	root = Tk()
	entry_list = gather_articles('cond-mat.mes-hall')
	my_gui = ArXivGui(root, entry_list)
	root.mainloop()

def test():
	totalDelta=0
	root = Tk()
	root.bind_all('<MouseWheel>', onEvent)
	root.mainloop()

if __name__ == '__main__':
	main()
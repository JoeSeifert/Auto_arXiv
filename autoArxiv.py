import urllib.request
import time
import datetime

"""
Auto-Arxiv v1.0
Purpose: Automatic arXiv searcher!
-Searches titles and abstracts for specified words of 1000 most recent articles
-Saves searches into a log for future use
-Allows searching of multiple terms together

Made by Joe Seifert
Python version 3.5.0

changelog:
-2018-06-28 -- added 'editQueryInLog()' to FullSearchLog class
			-- changed line in callAPI() so that it actually decoded in utf-8 instead of just converting a byte literal to a string. Yay newbie python mistakes.
-2018-06-27 -- added 'deleteFromLog()' to FullSearchLog class
"""

def callAPI(subsec):
	# makes API call, seaching for 500 most recent articles in a given subsection of arXiv (almost always cond-mat)
	# splits response up into separate entries
	base_url = 'http://export.arxiv.org/api/query?'
	q = 'search_query=cat:'+subsec+'&start=0&max_results=500&sortBy=submittedDate&sortOrder=descending'
	print('Url = {}'.format(base_url+q))
	response = urllib.request.urlopen(base_url+q).read()
	response = response.decode('utf8')
	#response = str(response)
	response = response.split('<entry>')
	return response

def parseAPIResponse(response,printPrompt=True):
	# could probably be better if I used regex...

	# parses through entries in the feed, using multiple 'switches' to start and stop recording labels / items
	# If you get really confused, future Joe, just turn on the print statement that's commented below and see what happens every loop.
	# Outputs list of dictionaries, where each dictionary contains information related to each article
	entrylist = []
	for entry in response:
		recording_label = False
		recording_item = False
		multiple_items = False
		entry_dict = {}
		label = ''
		item = ''
		ending = ''
		for i in entry:
			#print(i+ ' . recording_label='+str(recording_label)+'. recording_item='+str(recording_item)+'. ending = '+ending+'.')
			if i == '<' and not ending:
				#print('Recording label now')
				recording_label = True
				recording_item = False
				continue
			if i == '>' and not ending:
				#print('Finished recording label')
				recording_label = False
				recording_item = True
				ending = '</'+label+'>'
				if label in entry_dict:
					multiple_items = True
				continue
			if recording_label:
				label = label + i
			if recording_item:
				item = item + i
				if item.endswith(ending):
					item = item.replace(ending,'')
					recording_item = False
					if multiple_items:
						try:
							entry_dict[label].append(item)
							multiple_items = False
						except AttributeError:
							entry_dict[label] = [entry_dict[label]]
							entry_dict[label].append(item)
							multiple_items = False
					else:
						entry_dict[label] = item
					label = ''
					item = ''
					ending = ''
		entrylist.append(entry_dict)
	if printPrompt:
		print('-----Response has been parsed-----')
		print('Number of entries = '+str(len(entrylist)))
		print()
	return entrylist

def searchWord(feed,word):
	# seach keyword in abstract and title
	article_return_list = []
	for entry in feed:
		if word.lower() in entry['summary'].lower() or word.lower() in entry['title'].lower():
			article_return_list.append(entry)
	return article_return_list

def searchNewArticles(article_list,art_id):
	# finds all articles posted after a specified article (usually the last article seen)
	specified_id = numericID(art_id)
	new_list = []
	for article in article_list:
		art_id = article['id'].split('/abs/')[-1]
		art_id = numericID(art_id)
		if art_id > specified_id:
			new_list.append(article)
	return new_list

def searchAllWords(feed,words):
	# collects all articles that match each search term in the list 'words', and adds them to a list. Repeats are ommitted (Actually, I'm not sure if repeats are ommitted, but sortEntriesByDate takes care of that anyhow)
	# final_list = list of articles (dictioanries) that match the keywords
	final_list = []
	for word in words:
		art_list = searchWord(feed,word)
		for art in art_list:
			final_list.append(art)
	return final_list

def sortEntriesByDate(art_list):
		# sorts all entries in the list by date
		# omits repeats
		dateList = []
		IDList = []
		for entry in art_list:
			date = numericDate(entry['published'].split('T')[0])
			art_id = numericID(entry['id'].split('/abs/')[-1])
			dateList.append(date)
			IDList.append(art_id)

		# sorts entries 
		newIDList = []
		newDateList = []
		newEntryList = []
		addedToList = False
		for date,art_id,art in zip(dateList,IDList,art_list):
			# checks for duplicates
			if art_id in newIDList:
				continue

			# makes newIDList non-empty
			if len(newIDList) == 0:
				newIDList.append(art_id)
				newDateList.append(date)
				newEntryList.append(art)
				continue

			# does the sorting
			addedToList = False
			for pos,new_date in enumerate(newDateList):
				if date > new_date:
					newDateList.insert(pos,date)
					newIDList.insert(pos,art_id)
					newEntryList.insert(pos,art)
					addedToList = True
					break
			if not addedToList:
				newDateList.append(date)
				newIDList.append(art_id)
				newEntryList.append(art)
		return newEntryList

class FullSearchLog:

	def __init__(self,filename):
		self.filename = filename
		self.sdict = {} #dictionary of full searches :) [dict of dicts]
		self.readLog()

	def createFullSearch(self,label,queries,date,lastID,lastID2):
		# full searches are now just a dictionary
		fullSearch = {}
		fullSearch['queries'] = queries
		fullSearch['dateLastChecked'] = date
		fullSearch['lastIDSeen'] = lastID
		fullSearch['secondLastIDSeen'] = lastID2
		self.sdict[label] = fullSearch
		self.writeLog()

	def listSearchLabels(self):
		for i in self.sdict:
			print(i)

	def readLog(self):
		# reads the log and adds all searches to memory
		f = open(self.filename,'r+')
		#except FileNotFoundError:
		#	print('This error happened? You deleted your Search log, didn\'t you...')
		#	f = open(self.filename, 'w+')
		#	f.close()
		#	return

		lines = f.readlines()
		f.close()

		for num,line in enumerate(lines):
			if line.startswith('slabel'):
				label = lines[num].split('~*~')[1].replace('\n','')
				queryLabels = lines[num+1].split('~*~')[1].replace('\n','')
				queryLabels = queryLabels.split('///')
				dateLastChecked = lines[num+2].split('~*~')[1].replace('\n','')
				lastIDSeen = lines[num+3].split('~*~')[1].replace('\n','')
				lastIDSeen = int(lastIDSeen)
				secondLastIDSeen = lines[num+4].split('~*~')[1].replace('\n','')
				secondLastIDSeen = int(secondLastIDSeen)
				self.createFullSearch(label,queryLabels,dateLastChecked,lastIDSeen,secondLastIDSeen)

	def writeLog(self):
		# clears current log file, rewrites with current class info
		self.clearLogContents()
		f = open(self.filename,'w')
		for label in self.sdict:
			s = self.sdict[label]
			f.write('slabel~*~'+label+'\n')
			queryLine = ''
			for word in s['queries']:
				queryLine = queryLine + word + '///'
			queryLine = queryLine[0:len(queryLine)-3]
			f.write('queries~*~'+queryLine+'\n')
			f.write('dateLastChecked~*~'+s['dateLastChecked']+'\n')
			f.write('lastIDSeen~*~'+str(s['lastIDSeen'])+'\n')
			f.write('secondLastIDSeen~*~'+str(s['secondLastIDSeen'])+'\n')
		f.close()

	def deleteFromLog(self,label):
		try:
			del self.sdict[label]
		except KeyError:
			pass
		self.writeLog()

	def updateLog(self,slabel,date,lastID,lastID2):
		# do this at the end of any searching
		# updates one specific query, rewrites the log
		s = self.sdict[slabel] 
		s['dateLastChecked'] = date
		s['lastIDSeen'] = lastID
		s['secondLastIDSeen'] = lastID2
		self.writeLog()

	def editQueryInLog(self,slabel_start, slabel_end, queries):
		search = self.sdict[slabel_start] # does this make a reference or a copy? We shall find out...
		del self.sdict[slabel_start]
		search['queries'] = queries
		self.sdict[slabel_end] = search

	# helper functions below

	def clearLogContents(self):
		f = open(self.filename,'r+')
		f.truncate()
		f.close()

def printArticle(entry,printAbstract= False):
	# prints one article, straigh from dictionary input
	print('Title:  %s' % entry['title'])
	if printAbstract:
		print('Abstract: %s' % entry['summary'])
	print('arxiv-id: %s' % entry['id'])
	print('Published: %s' % entry['published'].split('T')[0])
	print(' ')

def printAllArticles(art_list, art_count= 100):
	# prints every article from a list of dictionaries
	count = 0
	for art in art_list:
		count += 1
		if count > art_count:
			break
		print('---------- Printing Article #{0} ----------'.format(count))
		printArticle(art)

# helper functions below

def numericDate(datestring):
	# YYYY-MM-DD format
	a = datestring.split('-')
	year = int(a[0])
	month = int(a[1])
	day = int(a[2])
	orderedDate = year*10000 + month*100 + day
	return orderedDate

def numericID(IDstring):
	# takes both string and int (i.e. numericID(numericID(ID)) works)
	# returns ID as a number, for sorting 
	try:
		ID = IDstring.split('v')[0]
		ID = ID.split('.')
		ID = int(ID[0])*100000 + int(ID[1])
	except AttributeError: # i.e. numeric ID was already given
		ID = IDstring
	return ID

def today():
	# returns date in YYYY-MM-DD
	d = datetime.datetime.now()
	d = str(d)
	d = d.split(' ')
	return d[0]

def isChemicalCompound(word):
	# determines if a search term is a chemical compound
	nums = '1234567890'
	for i in nums:
		if i in word:
			return True
	return False

def buildLatexEquiv(word):
	# builds a latex-equivalent of a word, in the case this was included in a title or abstract
	newWord = ''
	for pos,char in enumerate(word):
		if pos == 0:
			newWord = newWord + char
			continue
		try:
			subscr = int(char)
			newWord = newWord + '$_%i$' % (subscr)
		except ValueError:
			newWord = newWord + char
	return newWord

def findNewestID(art_list):
	# finds the article with the highest ID
	highestID = 0
	for entry in art_list:
		entryID = entry['id'].split('/abs/')[-1]
		entryID = numericID(entryID)
		if entryID > highestID:
			highestID = entryID
	return highestID

def main():
	print('ALL DONE!')

if __name__ == '__main__':
	main()
	
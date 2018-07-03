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
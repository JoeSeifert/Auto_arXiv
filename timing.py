from datetime import datetime

class Timing(object):
	"""
	Times how long each segment of code takes
	USING THIS: Create Timing object before the desired code, then call obj.conclude() at the end
	EX:

	x = Timing()

	<CODE TO EXECUTE>

	x.conclude()
	
	"""

	def __init__(self, message=''):
		self.current_time = datetime.now()
		self.start = self.current_time.hour*60*60 + self.current_time.minute*60 + self.current_time.second + self.current_time.microsecond/1000000
		self.end = 0
		self.message = message

	def endTiming(self):
		self.current_time = datetime.now()
		self.end = self.current_time.hour*60*60 + self.current_time.minute*60 + self.current_time.second + self.current_time.microsecond/1000000
		elapsedTime = self.end -self.start
		return(round(elapsedTime,3))

	def conclude(self):
		x = self.endTiming()
		if self.message == '':
			print('Selected code took {} seconds to compile'.format(x))
		else:
			print('{0} code took {1} seconds to compile'.format(self.message, str(x)))
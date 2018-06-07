class Version():
	def __init__(self):
		self.version = '1.0.6'

	def check(self):
		return True

	def execute(self):
		print(self.version)
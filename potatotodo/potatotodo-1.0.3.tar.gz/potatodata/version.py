class Version():
	def __init__(self):
		self.version = '1.0.3'

	def check(self):
		return True

	def execute(self):
		print(self.version)
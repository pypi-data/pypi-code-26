class k:
	def __init__(self, x):
		self.end = x

	def __repr__(self):
		return self.end.__repr__()

	def __matmul__(self, f):
		return self.end if (f == 'end' or f ==  0) else self.__class__(f(self.end))

	def __or__(self, f):
		return self.__matmul__(f)

	def also(self, block):
		block(self.end)
		return self.__class__(self.end)

	def let(self,f):
		return self.__class__(f(self.end))

	def run(block):
		return block()

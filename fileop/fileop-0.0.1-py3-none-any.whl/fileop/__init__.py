class file:
	def error(error):
		return ("\033["+str(31)+"m"+str(error)+"\033[0m")

	def create(name):
		"""file.create("file_name.txt")"""
		try:
			with open(name,'w') as f:
				f.write("")
				return True
		except Exception as e1:
			print (file.error(e1))
	
	def delete(name):
		"""file.delete("file_name.txt")"""
		try:
			import os
			os.remove(name)
			return True
		except Exception as e1:
			print (file.error(e1))
	
	def copy(name1,name2):
		"""file.copy("file_name1.txt","file_name2.txt")"""
		try:
			with open(name1,'r') as f1,open(name2,'w') as f2:
				f2.write(str(f1.read()))
				return True
		except Exception as e1:
			print (file.error(e1))
	#-------------read content of file-------------------------------
	def read(name):
		"""file.read("file_name.txt")"""
		try:
			with open(name) as f:
				return f.read()
		except Exception as e1:
			print (file.error(e1))
	#-----------------write to file----------------------------------
	def write(name,data):
		"""file.write("file_name.txt","data")"""
		try:
			with open(name,'w') as f:
				f.write(data)
		except Exception as e1:
			print (file.error(e1))
	#-------------------append to file------------------------------
	def append(name,data):
		"""file.append("file_name.txt","data")"""
		try:
			with open(name,'a') as f:
				f.write(data)
		except Exception as e1:
			print (file.error(e1))

class UserModel():
	def __init__(self, path, name, addr, filename_no_extension):
		self.path = path
		self.name = name
		self.addr = addr
		self.filename_no_extension = filename_no_extension

	def getSkeyPath(self):
		return f'{self.path}/{self.filename_no_extension}.skey'

	def uiString(self):
		return f'{self.name}:{self.addr}'
class PageHandler:

	def __init__(self):
		self.users = {}

	def addUser(self, user):
		self.users.setdefault(user.userName, user)

	def getUser(self, username):
		return self.users.get(username)

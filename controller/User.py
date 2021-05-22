from random_username.generate import generate_username


class User:

	def __init__(self, username=None, email=None, password=None, randomPlayer=False):
		self.activeGame = None
		self.gameHistory = []
		if randomPlayer:
			self.randomPlayer = randomPlayer
			self.userName = generate_username(1).pop()
		else:
			self.userName = username
			self.email = email
			self.password = password  # needs to be hashed
		pass

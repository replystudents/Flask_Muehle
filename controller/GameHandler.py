import uuid
from controller.Muehle import Muehle


class GameQueueObject:

	def __init__(self, gameId, player):
		self.player1 = player
		self.player2 = None
		self.gameId = gameId

	def registerPlayer(self, player):
		self.player2 = player


class GameHandler:

	def __init__(self):
		self.gameQueue = {}
		self.activeGames = {}

	def queueNewGame(self, user):
		gameId = uuid.uuid1()
		self.gameQueue.setdefault(gameId, GameQueueObject(gameId, user))
		return gameId

	def startGame(self, gameId):
		game = self.gameQueue.get(gameId)
		if game.player1 and game.player2:
			game = Muehle(game.player1, game.player2)
			self.activeGames.setdefault(gameId, game)
			self.gameQueue.pop(gameId)
			game.player1.user.activeGame = game
			game.player2.user.activeGame = game
			return game
		else:
			return Exception('Second Player not registered')

	def deleteGame(self, gameId):
		self.gameQueue.pop(gameId)
		game = self.activeGames.pop(gameId)
		if game is not None:
			game.player1.user.gameHistory.append(game)
			game.player2.user.gameHistory.append(game)

	def getGame(self, gameId):
		if self.gameQueue.get(gameId):
			return self.gameQueue.get(gameId)
		if self.activeGames.get(gameId):
			return self.activeGames.get(gameId)
		return Exception('Game not found')

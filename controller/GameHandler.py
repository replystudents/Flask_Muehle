"""
Author: Lorenz Adomat
"""
import uuid

from controller.Muehle import Muehle
from controller.DatabaseModels import db, Game, User
import json
import random
from typing import Union


# The GameQueueObject represents a new game, where one Player is waiting for another player
class GameQueueObject:

	def __init__(self, gameId, player):
		self.player1 = player
		self.player2 = None
		self.gameId = gameId

	def registerPlayer(self, player):
		self.player2 = player


# The GameHandler handles the games, which have not been started and the active games
class GameHandler:

	def __init__(self):
		self.gameQueue = {}
		self.activeGames = {}

	def queueNewGame(self, user):
		gameId = str(uuid.uuid1())
		self.gameQueue.setdefault(gameId, GameQueueObject(gameId, user))
		return gameId

	def startGame(self, gameId):
		game = self.gameQueue.get(gameId)
		if game.player1 and game.player2:
			# random user should start
			if bool(random.getrandbits(1)):
				game = Muehle(game.player1, game.player2)
			else:
				game = Muehle(game.player2, game.player1)
			self.activeGames.setdefault(gameId, game)
			self.gameQueue.pop(gameId)
			return game
		else:
			return Exception('Second Player not registered')

	def deleteGame(self, gameId):
		if self.gameQueue.get(gameId):
			self.gameQueue.pop(gameId)
		if self.activeGames.get(gameId):
			self.activeGames.pop(gameId)

	def getGame(self, gameId) -> Union[GameQueueObject, Muehle]:
		if self.gameQueue.get(gameId):
			return self.gameQueue.get(gameId)
		if self.activeGames.get(gameId):
			return self.activeGames.get(gameId)
		raise Exception('Game not found')

	def saveGameInDB(self, gameId):
		game = self.getGame(gameId)
		positions = game.positions
		dbGame = Game(gameId, game.player1.user.id, game.player2.user.id, game.winner.user.id if game.winner else None,
		              json.dumps(positions))
		db.session.add(dbGame)
		db.session.commit()
		self.deleteGame(gameId)

	def getActiveUserGames(self, user):
		games = []
		for gameId, game in self.activeGames.items():
			if game.player1.user.id == user.id or game.player2.user.id == user.id:
				games.append({
					"link": f"/game/{gameId}",
					"player1": game.player1.user.username,
					"player2": game.player2.user.username
				})
		return games

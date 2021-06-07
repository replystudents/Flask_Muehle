import uuid

from controller.Muehle import Muehle
from controller.DatabaseModels import db, Game, User
import json
import random
from typing import Union


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
			game.player1.user.setActiveGame(gameId)
			game.player2.user.setActiveGame(gameId)
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
		dbGame = Game(gameId, game.player1.user.id, game.player2.user.id, game.winner.user.id, json.dumps(positions))
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

	def getFinishedUserGames(self, user):
		games = []
		finishedGames = Game.query.filter((Game.playerId1 == user.id) | (Game.playerId2 == user.id)).all()
		for game in finishedGames:
			player1 = User.query.filter((User.id == game.playerId1)).first()
			player2 = User.query.filter((User.id == game.playerId2)).first()
			if player1 and player2:
				games.append({
					"player1": player1.username,
					"player2": player2.username,
					"resultP1": "1" if (game.winner and int(game.winner) == player1.id) else "0",
					"resultP2": "1" if (game.winner and int(game.winner) == player2.id) else "0",
					"date": f'{game.date.day}.{game.date.month}.{game.date.year}'

				})
		return games

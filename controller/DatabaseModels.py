"""
Author: Lorenz Adomat
"""
import datetime

from flask_sqlalchemy import SQLAlchemy
from random_username.generate import generate_username

db = SQLAlchemy(session_options={
	'expire_on_commit': False
})


class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(100))
	isTmpUser = db.Column(db.Boolean, default=False)
	isBot = db.Column(db.Boolean, default=False)

	def __init__(self, username=username, email=email, password=password, isTmpUser=isTmpUser, isBot=isBot):
		if isBot is True:
			self.username = 'Bot'
			self.isBot = isBot
		elif isTmpUser is True:
			self.username = generate_username(1).pop()
			self.isTmpUser = True
		else:
			self.username = username
			self.email = email
			self.password = password


class Game(db.Model):
	__tablename__ = 'game'
	gameId = db.Column(db.String(36), primary_key=True)
	playerId1 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	playerId2 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	winner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
	date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	positions = db.Column(db.JSON)

	def __init__(self, gameId, player1, player2, winner, positions):
		self.gameId = gameId
		self.playerId1 = player1
		self.playerId2 = player2
		self.winner = winner
		self.positions = positions


# queries Leaderboard from the database, which is used on the start-page
def getLeaderboard():
	leaderboardQuery = User.query.join(Game, (Game.winner == User.id)).add_columns(
		Game.winner).all()
	leaderboardUsers = {}
	for item in leaderboardQuery:
		if leaderboardUsers.get(item[0].username):
			update = {item[0].username: leaderboardUsers.get(item[0].username) + 1}
			leaderboardUsers.update(update)
		else:
			leaderboardUsers.setdefault(item[0].username, 1)

	leaderboard = []
	for key, value in leaderboardUsers.items():
		leaderboard.append((key, value))

	leaderboard.sort(key=lambda item: item[1], reverse=True)

	return leaderboard


# get all finished games of one user
def getFinishedUserGames(user):
	games = []
	finishedGames = Game.query.filter((Game.playerId1 == user.id) | (Game.playerId2 == user.id)).order_by(
		Game.date.desc()).all()
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


# get win/draw/loss statistics for one player
def getUserStatistics(user):
	draw = 0
	win = 0
	loss = 0
	userGames = getFinishedUserGames(user)
	for game in userGames:
		if game['resultP1'] == game['resultP2']:
			draw += 1
		elif game['resultP1'] == '1' and game['player1'] == user.username:
			win += 1
		elif game['resultP2'] == '1' and game['player2'] == user.username:
			win += 1
		else:
			loss += 1
	return (win, loss, draw)

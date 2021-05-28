from flask_sqlalchemy import SQLAlchemy
from random_username.generate import generate_username

db = SQLAlchemy()


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(100))
	isTmpUser = db.Column(db.Boolean, default=False)

	def __init__(self, username=username, email=email, password=password, isTmpUser=isTmpUser):
		if isTmpUser is True:
			self.username = generate_username(1).pop()
			self.isTmpUser = True
		else:
			self.username = username
			self.email = email
			self.password = password


class Game(db.Model):
	gameId = db.Column(db.String, primary_key=True)
	playerId1 = db.Column(db.String(100))
	playerId2 = db.Column(db.String(100))
	winner = db.Column(db.String)
	positions = db.Column(db.JSON)

	def __init__(self, player1, player2, winner, game):
		self.playerId1 = player1
		self.playerId2 = player2
		self.winner = winner
		self.game = game


def deleteTmpUsers():
	tmpUsers = User.query.filter_by(isTmpUser=True)
	db.session.delete(tmpUsers)
	db.commit()
	pass

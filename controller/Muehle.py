from collections import deque

board = [
	['X', ' ', ' ', 'X', ' ', ' ', 'X'],
	[' ', 'X', ' ', 'X', ' ', 'X', ' '],
	[' ', ' ', 'X', 'X', 'X', ' ', ' '],
	['X', 'X', 'X', ' ', 'X', 'X', 'X'],
	[' ', ' ', 'X', 'X', 'X', ' ', ' '],
	[' ', 'X', ' ', 'X', ' ', 'X', ' '],
	['X', ' ', ' ', 'X', ' ', ' ', 'X'],
]
states = {
	'init': 'INIT',
	'placePhase': 'PLACE_PHASE',
	'playingPhase': 'PLAYING_PHASE',
	'mill': 'MILL',
	'end': 'END'
}

number_of_pieces = 9


class Move:

	def __init__(self, player, token, pos_x=None, pos_y=None, place=False, delete=False):
		self.player = player
		self.token = token
		self.pos_x1 = token.pos_x
		self.pos_y1 = token.pos_y
		self.pos_x2 = pos_x
		self.pos_y2 = pos_y
		self.place = place
		self.delete = delete

		if place is True:
			self.move = f'{player.playerNumber}-set-{token.id} -> ({pos_x},{pos_y})'
		elif delete is True:
			self.move = f'{player.playerNumber}-del-{token.id}'
		else:
			self.move = f'{player.playerNumber}-mv-{token.id} - ({token.pos_x}, {token.pos_y}) -> ({pos_x},{pos_y})'


class Token:

	def __init__(self, player, number):
		self.player = player
		self.number = number
		self.id = player.playerNumber + '_' + str(number)
		self.pos_x = -1
		self.pos_y = -1

	def setPosition(self, x, y):
		self.pos_x = x
		self.pos_y = y

	def __str__(self):
		return self.id

	def __repr__(self):
		return f"Token({self.player} | {self.pos_x}, {self.pos_y})"


class Player:

	def __init__(self, user, PlayerNumber):
		self.startTokenList = deque()
		self.tokenList = []
		self.user = user
		self.playerNumber = PlayerNumber

	def getNumberOfTokens(self):
		return len(self.tokenList)


class Muehle:

	def __init__(self, user1, user2):
		self.player1 = Player(user1, 'P1')
		self.player2 = Player(user2, 'P2')

		self.activePlayer = self.player1
		self.winner = None

		self.board = board.copy()
		self.state = states['init']
		self.moves = []

		# Init Token List for both players
		for i in range(number_of_pieces):
			self.player1.startTokenList.append(Token(self.player1, i))
			self.player2.startTokenList.append(Token(self.player2, i))

		self.state = states['placePhase']

	def changePlayer(self) -> Player:
		if self.activePlayer == self.player1:
			self.activePlayer = self.player2
		else:
			self.activePlayer = self.player1

		return self.activePlayer

	def placeTokenOnBoard(self, token: Token, pos_x, pos_y):
		move = Move(self.activePlayer, token, pos_x, pos_y, place=True)
		if token in self.activePlayer.startTokenList:
			if self.board[pos_x][pos_y] == 'X':
				self.board[pos_x][pos_y] = token
				self.moves.append(move)
				token.setPosition(pos_x, pos_y)
				self.activePlayer.tokenList.append(token)
				self.activePlayer.startTokenList.remove(token)
				self.changePlayer()
			else:
				raise Exception('Bad position')
		else:
			raise Exception('Token was already placed')
		if len(self.player2.startTokenList) == 0:
			self.state = states['playingPhase']

	def isValidMove(self, token: Token, pos2_x, pos2_y) -> bool:
		move = Move(player=self.activePlayer, token=token, pos_x=pos2_x, pos_y=pos2_y)
		possibleMoves = self.getPossibleMoves()
		return any(m.move == move.move for m in possibleMoves)

	def isMill(self, player, token: Token) -> bool:
		x_pos = token.pos_x
		y_pos = token.pos_y
		if self.isRowComplete(x_pos, y_pos, player) or self.isColumnComplete(y_pos, x_pos, player):
			return True
		return False

	def isRowComplete(self, x, y, player: Player) -> bool:
		if x == 0 or x == 6:
			if self.board[x][0] != 'X' and self.board[x][3] != 'X' and self.board[x][
				6] != 'X' and self.board[x][0].player == player and self.board[x][3].player == player and self.board[x][
				6].player == player:
				return True
		elif x == 1 or x == 5:
			if self.board[x][1] != 'X' and self.board[x][3] != 'X' and self.board[x][
				5] != 'X' and self.board[x][1].player == player and self.board[x][3].player == player and self.board[x][
				5].player == player:
				return True
		elif x == 2 or x == 4:
			if self.board[x][2] != 'X' and self.board[x][3] != 'X' and self.board[x][
				4] != 'X' and self.board[x][2].player == player and self.board[x][3].player == player and self.board[x][
				4].player == player:
				return True
		elif x == 3:
			if y < 3 and self.board[x][0] != 'X' and self.board[x][1] != 'X' and self.board[x][
				2] != 'X' and y < 3 and self.board[x][0].player == player and self.board[x][1].player == player and \
					self.board[x][
						2].player == player:
				return True
			if y > 3 and self.board[x][4] != 'X' and self.board[x][5] != 'X' and self.board[x][
				6] != 'X' and y > 3 and self.board[x][4].player == player and self.board[x][5].player == player and \
					self.board[x][
						6].player == player:
				return True
		return False

	def isColumnComplete(self, y, x, player: Player) -> bool:
		if y == 0 or y == 6:
			if self.board[0][y] != 'X' and self.board[3][y] != 'X' and self.board[6][
				y] != 'X' and self.board[0][y].player == player and self.board[3][y].player == player and self.board[6][
				y].player == player:
				return True
		elif y == 1 or y == 5:
			if self.board[1][y] != 'X' and self.board[3][y] != 'X' and self.board[5][
				y] != 'X' and self.board[1][y].player == player and self.board[3][y].player == player and self.board[5][
				y].player == player:
				return True
		elif y == 2 or y == 4:
			if self.board[1][y] != 'X' and self.board[3][y] != 'X' and self.board[5][
				y] != 'X' and self.board[2][y].player == player and self.board[3][y].player == player and self.board[4][
				y].player == player:
				return True
		elif y == 3:
			if self.board[1][y] != 'X' and self.board[3][y] != 'X' and self.board[5][
				y] != 'X' and x < 3 and self.board[0][y].player == player and self.board[1][y].player == player and \
					self.board[2][
						y].player == player:
				return True
			if self.board[1][y] != 'X' and self.board[3][y] != 'X' and self.board[5][
				y] != 'X' and x > 3 and self.board[4][y].player == player and self.board[5][y].player == player and \
					self.board[6][
						y].player == player:
				return True
		return False

	def removeTokenFromBoard(self, token: Token):
		if self.state == states['mill']:
			x = token.pos_x
			y = token.pos_y
			self.board[x][y] = 'X'
			token.player.tokenList.remove(token)
			self.moves.append(Move(player=self.activePlayer, token=token, pos_x=x, pos_y=y, delete=True))
			token.setPosition(-1, -1)

		if token.player.getNumberOfTokens() < 3:
			self.winner = self.changePlayer()
			self.state = states['end']
		else:
			self.state = states['playingPhase']
			self.changePlayer()

	def getPossibleMoves(self) -> list[Move]:
		possibleMoves = []
		if self.state == states['placePhase']:
			# All free positions
			for i in range(len(self.board)):
				for j in range(len(self.board[i])):
					if self.board[i][j] == 'X':
						possibleMoves.append(
							Move(player=self.activePlayer, token=self.activePlayer.startTokenList[0], pos_x=i, pos_y=j,
							     place=True))
		elif self.state == states['mill']:
			# All tokens from opponent
			if self.activePlayer == self.player1:
				for token in self.player2.tokenList:
					possibleMoves.append(Move(player=self.activePlayer, token=token, delete=True))
		elif self.state == states['playingPhase']:
			tokens_of_player = self.activePlayer.tokenList
			for token in tokens_of_player:
				x = token.pos_x
				y = token.pos_y
				leftFieldX, leftFieldY = self.getLeftField(x, y)
				rightFieldX, rightFieldY = self.getRightField(x, y)
				topFieldX, topFieldY = self.getTopField(x, y)
				bottomFieldX, bottomFieldY = self.getBottomField(x, y)
				if leftFieldX and leftFieldY and board[leftFieldX][leftFieldY] == 'X':
					possibleMoves.append(
						Move(player=self.activePlayer, token=token, pos_x=leftFieldX, pos_y=leftFieldY))
				if rightFieldX and rightFieldY and board[rightFieldX][rightFieldY] == 'X':
					possibleMoves.append(
						Move(player=self.activePlayer, token=token, pos_x=rightFieldX, pos_y=rightFieldY))
				if topFieldX and topFieldY and board[topFieldX][topFieldY] == 'X':
					possibleMoves.append(Move(player=self.activePlayer, token=token, pos_x=topFieldX, pos_y=topFieldY))
				if bottomFieldX and bottomFieldY and board[bottomFieldX][bottomFieldY] == 'X':
					possibleMoves.append(
						Move(player=self.activePlayer, token=token, pos_x=bottomFieldX, pos_y=bottomFieldY))

		return possibleMoves

	def getLeftField(self, x, y):
		if (y == 0 or y == 6) and x != 0:
			return (x - 3, y)
		elif (y == 1 or y == 5) and x != 1:
			return (x - 2, y)
		elif (y == 2 or y == 4) and x != 2:
			return (x - 1, y)
		elif (y == 3) and y != 4 and x != 0:
			return (x - 1, y)
		else:
			return (-1, -1)

	def getRightField(self, x, y):
		if (y == 0 or y == 6) and x != 6:
			return (x + 3, y)
		elif (y == 1 or y == 5) and x != 5:
			return (x + 2, y)
		elif (y == 2 or y == 4) and x != 4:
			return (x + 1, y)
		elif (y == 3) and y != 2 and x != 6:
			return (x + 1, y)
		else:
			return (-1, -1)

	def getTopField(self, x, y):
		if (x == 0 or x == 6) and y != 0:
			return (x, y - 3)
		elif (x == 1 or x == 5) and y != 1:
			return (x, y - 2)
		elif (x == 2 or x == 4) and y != 2:
			return (x, y - 1)
		elif (x == 3) and y != 4 and y != 0:
			return (x, y - 1)
		else:
			return (-1, -1)

	def getBottomField(self, x, y):
		if (x == 0 or x == 6) and y != 6:
			return (x, y + 3)
		elif (x == 1 or x == 5) and y != 5:
			return (x, y + 2)
		elif (x == 2 or x == 4) and y != 4:
			return (x, y + 1)
		elif (x == 3) and y != 2 and y != 6:
			return (x, y + 1)
		else:
			return (-1, -1)

	def move(self, token: Token, pos_x, pos_y):
		if self.isValidMove(token, pos_x, pos_y):
			self.board[token.pos_x][token.pos_y] = 'X'
			self.board[pos_x][pos_y] = token
			self.moves.append(Move(self.activePlayer, token, pos_x, pos_y))
			token.setPosition(pos_x, pos_y)

			if self.isMill(self.activePlayer, token):
				self.state = states['mill']
			else:
				self.changePlayer()

	def getBoard(self):
		return self.board

	def undoLastMove(self):
		if len(self.moves) > 0:
			lastMove = self.moves.pop()
			if lastMove.place:
				player = lastMove.player
				token = lastMove.token
				player.startTokenList.appendleft(token)
				player.tokenList.remove(token)
				self.board[token.pos_x][token.pos_y] = 'X'
				token.setPosition(-1, -1)
				# if len(self.player1.startTokenList) == number_of_pieces and len(self.player2.startTokenList) == number_of_pieces:
				#	self.state = states['init']
				self.changePlayer()
				self.state = states['playingPhase']
			elif lastMove.delete:
				player = lastMove.token.player
				x = lastMove.pos_x
				y = lastMove.pos_y
				lastMove.token.setPosition(x, y)
				self.board[x][y] = lastMove.token
				player.tokenList.append(lastMove.token)
				self.state = states['mill']
				pass
			else:
				token = lastMove.token
				self.board[lastMove.pos_x2][lastMove.pos_y2] = 'X'
				self.board[lastMove.pos_x1][lastMove.pos_y1] = token
				token.setPosition(lastMove.pos_x1, lastMove.pos_y1)
				self.changePlayer()
				self.state = states['playingPhase']
		else:
			return
			raise Exception('No moves found to undo')


if __name__ == '__main__':
	muehle = Muehle('player1', 'player2')
	print(muehle.getPossibleMoves())
	print(muehle.getBoard())
	token = muehle.activePlayer.startTokenList[0]
	muehle.placeTokenOnBoard(token, 0, 0)
	muehle.placeTokenOnBoard(muehle.activePlayer.startTokenList[0], 0, 3)
	print(muehle.getBoard())

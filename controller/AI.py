from controller.Muehle import Muehle
from controller.Muehle import Player

points_for_mill = 2
points_for_token = 5
points_for_possible_move = .1


def getBestMove(game: Muehle, player: Player, depth):
	pass


def miniMax(game: Muehle, depth):
	pass


def min_move(game: Muehle, depth):
	possible_moves = game.getPossibleMoves()
	if depth == 0 or len(possible_moves) == 0:
		return rating(game)
	else:
		best_rating = float('inf')
		for move in possible_moves:
			move_rating = 0
			if game.state == 'PLACE_PHASE':
				x = move.pos_x2
				y = move.pos_y2
				game.placeTokenOnBoard(game.activePlayer.startTokenList[0], x, y)
				move_rating, _ = max_move(game, depth - 1)
				game.undoLastMove()
			elif game.state == 'PLAYING_PHASE':
				game.move(move.token, move.pos_x2, move.pos_y2)
				if game.isMill(game.activePlayer, move.token):
					move_rating = min_move(game, depth)
				else:
					move_rating, _ = max_move(game, depth - 1)
				game.undoLastMove()
			elif game.state == 'MILL':
				game.removeTokenFromBoard(move.token)
				move_rating, _ = max_move(game, depth - 1)
				game.undoLastMove()
			elif game.state == 'END':
				move_rating = -100  # player lost
			best_rating = min(move_rating, best_rating)
		return best_rating


def max_move(game: Muehle, depth):
	possible_moves = game.getPossibleMoves()
	if depth == 0 or len(possible_moves) == 0:
		return (rating(game), '')
	else:
		best_rating = float('-inf')
		best_move = None
		for move in possible_moves:
			move_rating = 0
			if game.state == 'PLACE_PHASE':
				x = move.pos_x2
				y = move.pos_y2
				game.placeTokenOnBoard(game.activePlayer.startTokenList[0], x, y)
				move_rating = min_move(game, depth - 1)
				game.undoLastMove()
			elif game.state == 'PLAYING_PHASE':
				game.move(move.token, move.pos_x2, move.pos_y2)
				if game.isMill(game.activePlayer, move.token):
					move_rating, _ = max_move(game, depth)
				else:
					move_rating = min_move(game, depth - 1)
				game.undoLastMove()
			elif game.state == 'MILL':
				game.removeTokenFromBoard(move.token)
				move_rating = min_move(game, depth - 1)
				game.undoLastMove()
			elif game.state == 'END':
				move_rating = 100  # player wins
			if move_rating > best_rating:
				best_rating = move_rating
				best_move = move
		return (best_rating, best_move)


def rating(game: Muehle):
	value = 0
	for token in game.activePlayer.tokenList:
		if game.isMill(game.activePlayer, token):
			value += points_for_mill

	for token in game.activePlayer.startTokenList:
		if game.isMill(game.activePlayer, token):
			value += points_for_mill

	value += len(game.activePlayer.tokenList) * points_for_token
	value += len(game.getPossibleMoves()) * points_for_possible_move
	return value


if __name__ == '__main__':
	muehle = Muehle('player1', 'player2')
	print(muehle.getPossibleMoves())
	print(muehle.getBoard())
	rating, move = max_move(muehle, 3)
	print(f'Rating: {rating}')
	print('Move: ')
	print(move.move)

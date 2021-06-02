from controller.Muehle import Muehle, Player, states

points_for_mill = 2
points_for_token = 10
points_for_possible_move = .1


def getBestMove(game: Muehle, player: Player, depth):
	_, best_move = max_move(game, depth, player)
	return best_move


def min_move(game: Muehle, depth, player):
	possible_moves = game.getPossibleMoves()
	if depth == 0 or len(possible_moves) == 0:
		game_rating = rating(game, player)
		return game_rating
	else:
		best_rating = float('inf')
		for move in possible_moves:
			move_rating = 0
			if game.state == states['placePhase']:
				game.executeMove(move, tmpMove=True)
				move_rating, _ = max_move(game, depth - 1, player)
				game.undoLastMove()
			elif game.state == states['playingPhase']:
				game.executeMove(move, tmpMove=True)
				if game.isMill(game.activePlayer, move.token):
					move_rating = min_move(game, depth, player)
				else:
					move_rating, _ = max_move(game, depth - 1, player)
				game.undoLastMove()
			elif game.state == states['mill']:
				game.executeMove(move, tmpMove=True)
				move_rating, _ = max_move(game, depth - 1, player)
				game.undoLastMove()
			elif game.state == states['end']:
				move_rating = -100  # player lost
			best_rating = min(move_rating, best_rating)
		return best_rating


def max_move(game: Muehle, depth, player):
	possible_moves = game.getPossibleMoves()
	if game.state == states['end']:
		return (-1, 'Game already finished')
	elif depth == 0 or len(possible_moves) == 0:
		return (rating(game, player), '')
	else:
		best_rating = float('-inf')
		best_move = None
		for move in possible_moves:
			move_rating = 0
			if game.state == states['placePhase']:
				game.executeMove(move, tmpMove=True)
				move_rating = min_move(game, depth - 1, player)
				game.undoLastMove()
			elif game.state == states['playingPhase']:
				game.executeMove(move, tmpMove=True)
				if game.isMill(game.activePlayer, move.token):
					move_rating, _ = max_move(game, depth, player)
				else:
					move_rating = min_move(game, depth - 1, player)
				game.undoLastMove()
			elif game.state == states['mill']:
				game.executeMove(move, tmpMove=True)
				move_rating = min_move(game, depth - 1, player)
				game.undoLastMove()
			elif game.state == states['end']:
				move_rating = 100  # player wins
			if move_rating > best_rating:
				best_rating = move_rating
				best_move = move
		return (best_rating, best_move)


def rating(game: Muehle, player):
	value = 0
	for token in player.tokenList:
		if game.isMill(player, token):
			pass
			value += points_for_mill

	for token in player.startTokenList:
		if game.isMill(player, token):
			pass
			value += points_for_mill

	if game.state == states['playingPhase']:
		diff = len(player.tokenList) - len(game.getOtherPlayer(player).tokenList)
		value += diff * points_for_token

	value += len(game.getPossibleMoves()) * points_for_possible_move
	if game.state == states['end']:
		value += 100 if game.winner == player else -100
	return value


if __name__ == '__main__':
	muehle = Muehle('player1', 'player2')
	muehle.printBoard()
	for i in range(25):
		print(f'Iteration: {i}')
		ai_rating, move = max_move(muehle, 3, muehle.activePlayer)
		print(f'Rating {move.player.playerNumber}: {ai_rating}')
		print(f'Move {move.player.playerNumber}: {move.move}')
		muehle.executeMove(move)
		muehle.printBoard()
		ai_rating, move = max_move(muehle, 3, muehle.activePlayer)
		print(f'Rating {move.player.playerNumber}: {ai_rating}')
		print(f'Move {move.player.playerNumber}: {move.move}')
		muehle.executeMove(move)
		muehle.printBoard()
		print(f'Tokens Player1: {len(muehle.player1.tokenList)}, Tokens Player2: {len(muehle.player2.tokenList)}')

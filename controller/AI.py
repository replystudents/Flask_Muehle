from controller.Muehle import Muehle, Player, states
import random

points_for_mill = 2
points_for_token = 10
points_for_possible_move = .1


def getBestMove(game: Muehle, player: Player, depth):
	_, best_move = max_move(game, depth, player)
	return best_move


def min_move(game: Muehle, depth, player):
	possible_moves = game.possibleMoves
	if depth == 0 or len(possible_moves) == 0 or game.state == states['end']:
		game_rating = rating(game, player, depth)
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
			best_rating = min(move_rating, best_rating)
		return best_rating


def max_move(game: Muehle, depth, player):
	possible_moves = game.possibleMoves
	if depth == 0 or len(possible_moves) == 0 or game.state == states['end']:
		return (rating(game, player, depth), '')
	else:
		best_rating = float('-inf')
		best_moves = []
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

			if move_rating == best_rating:
				best_moves.append(move)
			elif move_rating > best_rating:
				best_rating = move_rating
				best_moves = [move]
		return (best_rating, random.choice(best_moves))


def rating(game: Muehle, player, depth):
	value = 0
	for token in player.tokenList:
		if game.isMill(player, token):
			pass
			value += points_for_mill

	for token in player.startTokenList:
		if game.isMill(player, token):
			pass
			value += points_for_mill

	diff = len(player.tokenList) - len(game.getOtherPlayer(player).tokenList)
	value += diff * points_for_token

	value += len(game.getPossibleMoves()) * points_for_possible_move
	finished, winner = game.isGameFinished()
	if finished:
		if winner:
			value += 100 * (1 + depth) if winner == player else -100
		else:  # draw
			value += 100 * (
						1 + depth) if value < 0 else -100  # if own rating is less then rating of opponent, than it´s good to draw
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

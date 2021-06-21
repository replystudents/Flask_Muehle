from controller.Muehle import Muehle, Player, states
import random

points_for_mill = 2
points_for_token = 10
points_for_possible_move = .1
points_for_win = 200


def getBestMove(game: Muehle, player: Player, depth):
	if len(game.possibleMoves) >= 25:
		# otherwise computation time is to long
		depth -= 1
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
		return rating(game, player, depth), ''
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
		return best_rating, random.choice(best_moves)


def rating(game: Muehle, player, depth):
	value = 0
	finished, winner = game.isGameFinished()
	if finished:
		if winner:
			value += points_for_win * (1 + depth) if winner == player else -points_for_win
		else:  # draw
			value += points_for_win * (
					1 + depth) if value < 0 else -points_for_win  # if own rating is less then rating of opponent, than it´s good to draw
	else:
		for token in player.tokenList:
			if game.isMill(player, token):
				pass
				value += points_for_mill / 3

		for token in player.startTokenList:
			if game.isMill(player, token):
				pass
				value += points_for_mill / 3

		diff = (len(player.tokenList) + len(player.startTokenList)) - (
				len(game.getOtherPlayer().startTokenList) + len(game.getOtherPlayer(player).tokenList))
		value += diff * points_for_token
		if player == game.activePlayer:
			value += len(game.possibleMoves) * points_for_possible_move
		else:
			value -= len(game.possibleMoves) * points_for_possible_move  # possible moves for opponent
	return value

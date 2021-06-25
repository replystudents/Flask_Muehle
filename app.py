"""
Author: Gideon Weber & Lorenz Adomat
"""

from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from controller.DatabaseModels import db, User, getLeaderboard, getFinishedUserGames, getUserStatistics
from controller.GameHandler import GameHandler, GameQueueObject
from controller.Muehle import Muehle, Move
from controller.AI import getBestMove
import os

app = Flask(__name__)
app.secret_key = "secret_key_for_the_sessions"
basedir = os.path.abspath(
    os.path.dirname(
        __file__
    )
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "MuehleDB.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db.create_all(app=app)

# async_mode = "treading" because otherwise different user sessions influence each other
# without it would lead to performance issues when the minimax Algorithm is calculating
socketio = SocketIO(app, async_mode="threading")
gameHandler = GameHandler()


# get the user of the current session
def getUser():
    if "username" in session:
        username = session["username"]
        user = User.query.filter_by(username=username).first()
        if user:
            return user
    user = User(isTmpUser=True)
    db.session.add(user)
    db.session.commit()
    session["username"] = user.username
    return user


# route: main page
@app.route('/')
def main_page():
    user = getUser()
    active_games = gameHandler.getActiveUserGames(user)
    game_history = getFinishedUserGames(user)
    leaderboard = getLeaderboard()
    statistics = getUserStatistics(user)
    return render_template('main.html', user=user, active_games=active_games, game_history=game_history,
                           leaderboard=leaderboard, statistics=statistics)


# route: rules page
@app.route('/rules')
def rules_page():
    user = getUser()
    return render_template('rules.html', user=user)


# route: game page without gameid (to start a new game)
@app.route('/game/', methods=['POST', 'GET'])
def game():
    user = getUser()
    if request.method == 'POST':
        gameid = gameHandler.queueNewGame(user)
        if request.form['gametype'] == 'bot':
            bot = User.query.filter(User.isBot == True).first()
            if bot is None:
                bot = User(isBot=True)
                db.session.add(bot)
                db.session.commit()
            gameHandler.getGame(gameid).registerPlayer(bot)
        return redirect('/game/' + str(gameid) + '/')

    else:
        return render_template('game.html', user=user, newgame=True)


# route: game page with gameid
@app.route('/game/<gameid>/')
def game_page(gameid=None):
    user = getUser()
    if gameid:
        try:
            game = gameHandler.getGame(gameid)
        except Exception:
            return redirect('/game/')
        if isinstance(game, Muehle):  # if it´s an active game
            if game.player1.user.id == user.id or game.player2.user.id == user.id:
                return render_template('game.html', user=user, gameid=gameid)
            else:
                return redirect('/game/')
        if isinstance(game, GameQueueObject) and game.player1.id != user.id:  # if it´s a game, which has not started
            game.registerPlayer(user)
        return render_template('game.html', user=user, gameid=gameid)
    else:
        return redirect('/game/')


# route: history page
@app.route('/history')
def history_page():
    user = getUser()
    game_history = gameHandler.getFinishedUserGames(user)
    return render_template('history.html', user=user, game_history=game_history)


# socket: send Username to Client when the SocketIO connection is established
@socketio.on('connected')
def on_connected(data):
    emit('username', str(getUser().username))


# socket: client requests to join a game based on the gameid in their url
@socketio.on('join')
def on_join(data):
    username = getUser().username
    room = data['gameid']
    join_room(room)
    try:
        game = gameHandler.getGame(data['gameid'])
    except Exception:
        leave_room(room)
        return redirect('/game/')

    if isinstance(game, GameQueueObject) and game.player2 and game.player2.isBot:
        gameSession = gameHandler.startGame(data['gameid'])
        # if bot is first player, it has to make the first move
        emit('startGame', buildGameObject(gameSession),
             to=room)
        if gameSession.activePlayer.user.isBot:
            executeBotMove(gameSession, data['gameid'])
    # if a second player has joined, the game can be started
    elif isinstance(game, GameQueueObject) and game.player2:
        gameSession = gameHandler.startGame(data['gameid'])
        emit('startGame', buildGameObject(gameSession), to=room)
    elif isinstance(game, Muehle):
        emit('startGame', buildGameObject(game), to=room),
    else:
        send('Verbindung zu ' + username + 'aufgebaut.', to=room)


# socket: player wants to place a token on the board
@socketio.on('placeToken')
def on_placeToken(data):
    gameSession = gameHandler.getGame(data['gameid'])
    try:
        if gameSession.player1.user.id == getUser().id:
            move = gameSession.placeTokenOnBoard(gameSession.player1.startTokenList[0], int(data["pos_x"]),
                                                 int(data["pos_y"]))
        elif gameSession.player2.user.id == getUser().id:
            move = gameSession.placeTokenOnBoard(gameSession.player2.startTokenList[0], int(data["pos_x"]),
                                                 int(data["pos_y"]))
        else:
            # Unknown Player wants to make a move
            return

        emit('tokenPlaced', buildGameObject(gameSession, move=move), to=data['gameid'])

        # if bot has to make a move
        while gameSession.activePlayer.user.isBot and gameSession.state != 'END':
            executeBotMove(gameSession, data['gameid'])

        if gameSession.state == 'END':
            gameHandler.saveGameInDB(data['gameid'])
    except Exception as err:
        emit('ErrorPlacing', buildGameObject(gameSession, error=err), to=data['gameid'])


# socket: player wants to move a token on board
@socketio.on('moveToken')
def on_moveToken(data):
    gameSession = gameHandler.getGame(data['gameid'])
    try:
        if gameSession.player1.user.id == getUser().id:
            move = gameSession.move(gameSession.player1.getToken(int(data["token"])), int(data["pos_x"]),
                                    int(data["pos_y"]))
        elif gameSession.player2.user.id == getUser().id:
            move = gameSession.move(gameSession.player2.getToken(int(data["token"])), int(data["pos_x"]),
                                    int(data["pos_y"]))
        else:
            # Unknown Player wants to make a move
            return

        emit('tokenMoved', buildGameObject(gameSession, move), to=data['gameid'])

        while gameSession.activePlayer.user.isBot and gameSession.state != 'END':
            executeBotMove(gameSession, data['gameid'])

        if gameSession.state == 'END':
            gameHandler.saveGameInDB(data['gameid'])
    except Exception as err:
        emit('ErrorMoving', buildGameObject(gameSession, error=err), to=data['gameid'])


# socket: player wants to remove a token
@socketio.on('removeToken')
def on_removeToken(data):
    gameSession = gameHandler.getGame(data['gameid'])
    try:
        if gameSession.player1.user.id == getUser().id:
            move = gameSession.removeTokenFromBoard(gameSession.player2.getToken(int(data["token"])))
        elif gameSession.player2.user.id == getUser().id:
            move = gameSession.removeTokenFromBoard(gameSession.player1.getToken(int(data["token"])))
        else:
            # Unknown Player wants to make a move
            return

        emit('tokenRemoved', buildGameObject(gameSession, move=move), to=data['gameid'])

        while gameSession.activePlayer.user.isBot and gameSession.state != 'END':
            executeBotMove(gameSession, data['gameid'])
        if gameSession.state == 'END':
            gameHandler.saveGameInDB(data['gameid'])
    except Exception as err:
        emit('ErrorRemoving', buildGameObject(gameSession, error=err), to=data['gameid'])


# socket: client leaves the socketIO room, when the game is finished or the event beforeunload fires
@socketio.on('leave')
def on_leave(data):
    username = getUser().username
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)


# socket: client wants to get the up-to-date board
@socketio.on('syncGame')
def on_syncGame(data):
    gameSession = gameHandler.getGame(data['gameid'])
    data['board'] = gameSession.positions[-1]
    emit('syncGame', data, to=data['gameid'])


# socket: player requests to end the game in a tie
@socketio.on('tieGame')
def on_tieGame(data):
    gameSession = gameHandler.getGame(data['gameid'])
    if gameSession.player1.user.id == getUser().id:
        gameSession.player1.tie = True
    elif gameSession.player2.user.id == getUser().id:
        gameSession.player2.tie = True
    else:
        # Unknown Player wants to tie
        return

    if gameSession.player1.tie and gameSession.player2.tie:
        gameSession.winner = None
        gameSession.state = 'END'
        emit('updateGameState', buildGameObject(gameSession), to=data['gameid'])
        gameHandler.saveGameInDB(data['gameid'])
    else:
        emit('wantsToTie', to=data['gameid'])


# socket: player wants to surrender
@socketio.on('surrenderGame')
def on_surrenderGame(data):
    gameSession = gameHandler.getGame(data['gameid'])
    if gameSession.player1.user.id == getUser().id:
        gameSession.winner = gameSession.player2
    elif gameSession.player2.user.id == getUser().id:
        gameSession.winner = gameSession.player1
    else:
        # Unknown Player wants to surrender
        return

    gameSession.state = 'END'
    emit('updateGameState', buildGameObject(gameSession), to=data['gameid'])
    gameHandler.saveGameInDB(data['gameid'])


# execute a bot move and update the players game state
def executeBotMove(gameSession, room):
    move = getBestMove(gameSession, gameSession.activePlayer, 3)
    if isinstance(move, Move):
        gameSession.executeMove(move)
        botMoveObject = buildGameObject(gameSession, move=move)
        if move.delete:
            emit('tokenRemoved', botMoveObject, to=room)
        elif move.place:
            emit('tokenPlaced', botMoveObject, to=room)
        else:
            emit('tokenMoved', botMoveObject, to=room)


# build an object from gamedata that can be send to the players
def buildGameObject(gamedata, move=None, error=None):
    gameObject = {
        'activePlayer': gamedata.activePlayer.user.username,
        'player1': gamedata.player1.user.username,
        'player2': gamedata.player2.user.username,
        'state': gamedata.state
    }
    if move and isinstance(move, Move):
        if move.delete:
            if move.player.playerNumber == 'P1':
                gameObject['player'] = 'player2'
            else:
                gameObject['player'] = 'player1'
        else:
            if move.player.playerNumber == 'P1':
                gameObject['player'] = 'player1'
            else:
                gameObject['player'] = 'player2'
        gameObject['pos_x'] = move.pos_x2
        gameObject['pos_y'] = move.pos_y2
        gameObject['tokenid'] = f'{gameObject["player"]}-{move.token.id.split("_")[1]}'
    if gamedata.winner:
        gameObject['winner'] = gamedata.winner.user.username

    if error and isinstance(error, Exception):
        gameObject['error'] = error.args[0]
    return gameObject


# run flask server
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')

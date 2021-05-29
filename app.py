from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from controller.GameHandler import GameHandler
from controller.User import User
from controller.PageHandler import PageHandler

app = Flask(__name__)
app.secret_key = "secret_key_for_the_sessions"
socketio = SocketIO(app)
pageHandler = PageHandler()
gameHandler = GameHandler()


def getUser():
    if "username" in session:
        username = session["username"]
        user = pageHandler.getUser(username)
        if user:
            return user

    user = User(randomPlayer=True)
    pageHandler.addUser(user)
    session["username"] = user.userName
    return user


@app.route('/')
def main_page():
    user = getUser()
    return render_template('index.html', user=user)


@app.route('/impressum')
def impressum_page():
    user = getUser()
    return render_template('impressum.html', user=user)


@app.route('/contact')
def contact_page():
    user = getUser()
    return render_template('contact.html', user=user)


@app.route('/game/', methods=['POST', 'GET'])
def game():
    user = getUser()
    if request.method == 'POST':
        print(request.form['gametype'])
        gameid = gameHandler.queueNewGame(user)

        return redirect('/game/' + str(gameid) + '/')
    else:
        return render_template('game.html', user=user, newgame=True)


@app.route('/game/<gameid>/')
def game_page(gameid=None):
    user = getUser()
    if gameid:
        game = gameHandler.getGame(gameid)
        print(type(game))
        if type(game) == type(Exception()):
            if game.args[0] == 'Game not found':
                return redirect('/game/')
        if game.player1 != user:
            print('REGISTERING PLAYER')
            game.registerPlayer(user)
            # gameHandler.startGame(gameid)
            print("READY TO START GAME")
        user = getUser()
        return render_template('game.html', user=user, gameid=gameid)
    else:
        return redirect('/game/')


@app.route('/history')
def history_page():
    user = getUser()
    return render_template('history.html', user=user)


# @socketio.on('message')
# def handle_message(data):
#     print('received message: ' + data)
#
#
# @socketio.on('json')
# def handle_json(json):
#     print('received json: ' + str(json))


@socketio.on('connected')
def handle_my_custom_event(json):
    emit('game', str(getUser().userName))


# @socketio.on('validate move')
# def validateMove():
#     print('validateMove')
#
#     emit('gameUpdated', 'gameUpdated')


@socketio.on('join')
def on_join(data):
    print(data)
    username = getUser().userName  # data['username']
    room = data['gameid']
    join_room(room)

    game = gameHandler.getGame(data['gameid'])

    if game.player2:
        print('START GAME')
        print('player1', game.player1)
        print('player2', game.player2)
        gamesession = gameHandler.startGame(data['gameid'])

        emit('startGame', buildGameObject(gamesession),
             to=room)
    else:
        send('Verbindung zu ' + username + 'aufgebaut.', to=room)


@socketio.on('placeTokenOnBoard')
def on_placeToken(data):
    gamesession = gameHandler.getGame(data['gameid'])
    res = ''
    if gamesession.player1.user == getUser():
        res = gamesession.placeTokenOnBoard(gamesession.player1.startTokenList[0], int(data["pos_x"]),
                                            int(data["pos_y"]))
    else:
        res = gamesession.placeTokenOnBoard(gamesession.player2.startTokenList[0], int(data["pos_x"]),
                                            int(data["pos_y"]))
    if res == None:
        print('nextMove')
        object = buildGameObject(gamesession)
        object['player'] = data['player']
        object['pos_x'] = data['pos_x']
        object['pos_y'] = data['pos_y']
        emit('tokenPlaced', object, to=data['gameid'])
    else:
        print('Error')
        emit('ErrorPlacing', buildGameObject(gamesession), to=data['gameid'])


@socketio.on('moveToken')
def on_moveToken(data):
    print("moveToken")
    gamesession = gameHandler.getGame(data['gameid'])
    res = ''
    if gamesession.player1.user == getUser():
        res = gamesession.move(gamesession.player1.tokenList[int(data["token"])], int(data["pos_x"]),
                               int(data["pos_y"]))
    else:
        res = gamesession.move(gamesession.player2.tokenList[int(data["token"])], int(data["pos_x"]),
                               int(data["pos_y"]))
    print(res)
    print('moveToken')
    object = buildGameObject(gamesession)
    object['player'] = data['player']
    object['pos_x'] = data['pos_x']
    object['pos_y'] = data['pos_y']
    object['tokenid'] = data['tokenid']
    emit('tokenMoved', object, to=data['gameid'])


# @socketio.on('leave')
# def on_leave(data):
#     username = data['username']
#     room = data['room']
#     leave_room(room)
#     send(username + ' has left the room.', to=room)

def buildGameObject(gamedata):
    return {'activePlayer': gamedata.activePlayer.user.userName,
            'player1': gamedata.player1.user.userName, 'player2': gamedata.player2.user.userName,
            'state': gamedata.state}


if __name__ == '__main__':
    # app.run()
    socketio.run(app)

from flask import Flask, render_template, request, session, redirect
# from flask_socketio import SocketIO
from controller.GameHandler import GameHandler
from controller.User import User
from controller.PageHandler import PageHandler

app = Flask(__name__)
app.secret_key = "secret_key_for_the_sessions"
# socketio=SocketIO(app)
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

        return redirect('/game/'+str(gameid)+'/')
    else:
        return render_template('game.html', user=user, newgame=True)


@app.route('/game/<gameid>/')
def game_page(gameid=None):
    user = getUser()
    if gameid:
        print(gameid)
        game = gameHandler.getGame(gameid)
        if game.player1:
            game.registerPlayer(user)
            gameHandler.startGame(gameid)
        print(game.player1)
        user = getUser()
        return render_template('game.html', user=user, gameid=gameid)
    else:
        return redirect('/game/')


@app.route('/history')
def history_page():
    user = getUser()
    return render_template('history.html', user=user)


if __name__ == '__main__':
    app.run()
    # socketio.run(app)

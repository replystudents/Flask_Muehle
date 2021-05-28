from flask import Flask, render_template, request, session, redirect
from controller.DatabaseModels import db, User, Game

# from flask_socketio import SocketIO

from controller.GameHandler import GameHandler

app = Flask(__name__)
app.secret_key = "secret_key_for_the_sessions"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/muehle_db.sqlite'  # might be different in windows
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db.create_all(app=app)
# socketio=SocketIO(app)

gameHandler = GameHandler()


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

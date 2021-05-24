from flask import Flask, render_template, request, session
from controller.GameHandler import GameHandler
from controller.User import User
from controller.PageHandler import PageHandler

app = Flask(__name__)
app.secret_key = "secret_key_for_the_sessions"
pageHandler = PageHandler()
gameHandler = GameHandler()


@app.route('/')
def main_page():
	if "username" in session:
		username = session["username"]
		user = pageHandler.getUser(username)
		if user:
			return render_template('index.html', user=user)

	user = User(randomPlayer=True)
	pageHandler.addUser(user)
	session["username"] = user.userName
	return render_template('index.html', user=user)


@app.route('/impressum')
def impressum_page():
	if "username" in session:
		username = session["username"]
		user = pageHandler.getUser(username)
		if user:
			return render_template('impressum.html', user=user)

	user = User(randomPlayer=True)
	pageHandler.addUser(user)
	session["username"] = user.userName
	return render_template('impressum.html', user=user)


@app.route('/contact')
def contact_page():
	if "username" in session:
		username = session["username"]
		user = pageHandler.getUser(username)
		if user:
			return render_template('contact.html', user=user)

	user = User(randomPlayer=True)
	pageHandler.addUser(user)
	session["username"] = user.userName
	return render_template('contact.html', user=user)


@app.route('/game/<id>')
def game_page():
	return render_template('game.html')


@app.route('/history')
def history_page():
	if "username" in session:
		username = session["username"]
		user = pageHandler.getUser(username)
		if user:
			return render_template('history.html', user=user)

	user = User(randomPlayer=True)
	pageHandler.addUser(user)
	session["username"] = user.userName
	return render_template('history.html', user=user)


if __name__ == '__main__':
	app.run()

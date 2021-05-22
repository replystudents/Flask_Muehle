from flask import Flask, render_template, request, make_response
from controller.GameHandler import GameHandler
from controller.User import User
from controller.PageHandler import PageHandler

app = Flask(__name__)
pageHandler = PageHandler()
gameHandler = GameHandler()


@app.route('/')
def main_page():
	username = request.cookies.get('userName')
	if username:
		user = pageHandler.getUser(username)
		if user:
			return render_template('index.html', user=user)

	user = User(randomPlayer=True)
	pageHandler.addUser(user)
	resp = make_response(render_template('index.html', user=user))
	resp.set_cookie('userName', user.userName)
	return resp


@app.route('/impressum')
def impressum_page():
	username = request.cookies.get('userName')
	if username:
		user = pageHandler.getUser(username)
		if user:
			return render_template('impressum.html', user=user)

	user = User(randomPlayer=True)
	pageHandler.addUser(user)
	resp = make_response(render_template('impressum.html', user=user))
	resp.set_cookie('userName', user.userName)
	return resp


@app.route('/contact')
def contact_page():
	username = request.cookies.get('userName')
	if username:
		user = pageHandler.getUser(username)
		if user:
			return render_template('contact.html', user=user)

	user = User(randomPlayer=True)
	pageHandler.addUser(user)
	resp = make_response(render_template('contact.html', user=user))
	resp.set_cookie('userName', user.userName)
	return resp


@app.route('/game/<id>')
def game_page():
	return render_template('game.html')


@app.route('/history')
def history_page():
	username = request.cookies.get('userName')
	if username:
		user = pageHandler.getUser(username)
		if user:
			return render_template('history.html', user=user)

	user = User(randomPlayer=True)
	pageHandler.addUser(user)
	resp = make_response(render_template('history.html', user=user))
	resp.set_cookie('userName', user.userName)
	return resp


if __name__ == '__main__':
	app.run()

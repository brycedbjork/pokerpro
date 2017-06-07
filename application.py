from back import *

from flask import Flask, jsonify, render_template, request, url_for

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
	@app.after_request
	def after_request(response):
		response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
		response.headers["Expires"] = 0
		response.headers["Pragma"] = "no-cache"
		return response


@app.route("/")
def index():
	"""Home page with description of site, links, and pictures"""
	return render_template("index.html")


@app.route("/odds/")
def odds():
	"""Returns offs given submitted hand"""
	# check proper method
	if request.method == "GET":
		# check if cards arg exists
		hand = json.loads(request.args["cards"])
		hand_type = request.args["hand_type"]
		return_odds = analyze(hand=hand, hand_type=hand_type)
		print(return_odds)
		return jsonify(return_odds)
	# else return empty list
	return jsonify([])


@app.route("/learn/")
def learn():
	"""Learn page with interactive hand selection and odds updating"""
	return render_template("learn.html")


@app.route("/play/")
def play():
	"""Game based on guessing the calculable probabilities"""
	return render_template("play.html")


if __name__ == "__main__":
	app.run()

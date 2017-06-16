# coding=utf-8
from flask import Flask, request, url_for, render_template
from .api import classifier
from flask import jsonify
app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')

@app.route("/search", methods=['GET'])
def main():
	query = request.args.get('query', default=None)
	if query=="" or query is None:
		return ""
	else:
		print(query)
		return jsonify(classifier.verify(query))
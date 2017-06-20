# coding=utf-8
from flask import Flask, request, url_for, render_template, session
import uuid
from .api import classifier
from flask import jsonify
app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')

@app.route("/search", methods=['GET'])
def main():
	query = request.args.get('query', default=None)
	if 'uuid' in session:
		uid = session['uuid']
	else:
		uid = str(uuid.uuid4())
		session['uuid'] = uid

	if query=="" or query is None:
		return ""
	else:
		print(query)
		return jsonify(classifier.verify(query, uid))

@app.route("/clear", methods=['GET'])
def clear():
	if 'uuid' in session:
		uid = session['uuid']
		session.pop('uuid', None)
		classifier.clear_data(uid)
	return "succeed"
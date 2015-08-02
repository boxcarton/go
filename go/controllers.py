import os

from flask import Flask, request, Response, g, redirect
from flask import render_template, url_for, send_from_directory
from flask import make_response, abort, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

from go import app

from go.core import api_manager
from go.models import Redirects

for model_name in app.config['API_MODELS']:
  model_class = app.config['API_MODELS'][model_name]
  api_manager.create_api(model_class, methods=['GET', 'POST', 'PUT', 'DELETE'])

session = api_manager.session
db = SQLAlchemy(app)

# routing for basic pages (pass routing onto the Angular app)
@app.route('/')
def index(**kwargs):
  return make_response(open('go/templates/index.html').read())

@app.route('/a/<name>/<url>')
def add_url(name, url):
  print name + ":" + url

@app.route('/<name>', methods=['GET'])
def get_url(name):
  rd = Redirects.query.filter_by(name=name).one()
  if rd is not None:
    rd.num_visits = rd.num_visits + 1
    rd.name = "CHANGED"
    db.session.commit()
    return redirect(rd.url, code=302)
  return redirect(url_for('index'), code=302)

# special file handlers and error handlers
@app.route('/favicon.ico')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
         'img/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

from . import api
from .. import core

import flask
import os
import peewee

front_end = flask.Blueprint("front-end", __name__)

@front_end.route("/")
def index():
    return flask.current_app.send_static_file("index.html")

@front_end.route("/pictures")
def pictures():
    return flask.current_app.send_static_file("index.html")

@front_end.route("/people")
def people():
    return flask.current_app.send_static_file("index.html")

@front_end.route("/people/<int:id>")
def person(id):
    return flask.current_app.send_static_file("index.html")

def main():
    src_dir_path = os.getcwd()

    db = peewee.SqliteDatabase(os.path.join(src_dir_path, "pichore.db"))

    model = core.model.create(db)

    app = flask.Flask(__name__)
    app.register_blueprint(front_end, url_prefix="/")
    app.register_blueprint(api.api, url_prefix="/api")

    @app.before_request
    def before_request():
        flask.g.model = model
        flask.g.src_dir_path = src_dir_path
        return None

    @app.after_request
    def after_request(response):
        flask.g.src_dir_path = None
        flask.g.model = None
        return response

    app.run(threaded=True)

import os

from flask import Flask

from flaskr import api, db
from flaskr.utils import cr_api


def create_app():

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    cr_api.init_app(app)

    app.register_blueprint(api.blueprint)

    return app

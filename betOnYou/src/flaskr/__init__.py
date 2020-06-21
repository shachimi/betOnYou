import os

from flask import Flask

from . import api, db, utils


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    utils.init_app(app)

    app.register_blueprint(api.blueprint)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        c = db.get_db().cursor()
        c.execute('select * from player')
        result = c.fetchall()
        print(result)
        print(result)
        print(app.config['API_SECRET'])
        return 'Hello, World! %s' % result

    return app

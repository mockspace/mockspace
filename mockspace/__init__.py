import os
import subprocess

from flask import Flask

from mockspace.db import get_db


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "mockspace.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    # and initializes the database on first launch
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    else:
        os.environ["FLASK_APP"] = "mockspace"
        subprocess.run('flask init-db', shell=True)

    # register the database commands
    from mockspace import db

    db.init_app(app)

    # apply the blueprints to the app
    from mockspace import auth, services, methods

    app.register_blueprint(auth.bp)
    app.register_blueprint(services.bp)
    app.register_blueprint(methods.bp)

    # make url_for('index') == url_for('service.index')
    app.add_url_rule("/", endpoint="index")

    return app

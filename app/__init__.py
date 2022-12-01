import os

from werkzeug.debug import DebuggedApplication
from flask import Flask, render_template, send_from_directory

# база данных
# from flask_migrate import Migrate, current
#from flask_bootstrap import Bootstrap

from config import Config, loggingConfig
import app.logging_utils

logging_utils.init_logger(Config.LOGGING_FILE, loggingConfig)

from app.database import db_session


# db = SQLAlchemy()
# migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile('config.py', silent=True)
        # or from CLass (needs to be imported from module)
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # managing db sessions
    app.db_session = db_session

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    # инициализация базы данных
    # db.init_app(app)
    # migrate.init_app(app, db)

    # blueprint для главной
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # blueprint для поиска
    from app.search import bp as search_bp
    app.register_blueprint(search_bp)

    # blueprint для ошибок
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory('app/', 'favicon.ico')

    return app


from app import models

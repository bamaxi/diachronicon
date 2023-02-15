import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    BASEDIR = basedir

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'constructicon-now-with-history-wow'

    # DATABASE = os.path.join(app.instance_path, 'app.sqlite')
    SQLALCHEMY_DATABASE_URI_TEMPLATE = 'sqlite:///' + basedir + '{}'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'diachronicon.db')
    # sqlalchemy_echo = os.environ.get('SQLA_ECHO')
    # SQLALCHEMY_ECHO = bool(int(os.environ.get('SQLA_ECHO') or 0)) or 'debug'
    SQLALCHEMY_ECHO = 'debug'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JINJA_OPTIONS = {
        # "extensions": ["jinja2.ext.autoescape", "jinja2.ext.with_"],
        # 'line_statement_prefix': '%',
        'trim_blocks': True, 'lstrip_blocks': True
    }

    LOGGING_FILE = os.environ.get('FLASK_LOGGING_FILE') or 'logs/base.log'


class TestConfig(Config):
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOGGING_FILE = os.environ.get('FLASK_LOGGING_FILE') or 'logs/test.log'


loggingConfig = {
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default',
        },
        'file': {
         'class': 'logging.handlers.RotatingFileHandler',
         'filename': Config.LOGGING_FILE,
         'encoding': 'utf-8',
         'maxBytes': 8*2**23,  # 8MB
         'backupCount': 5,
         'formatter': 'default',
         'level': 'INFO'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi', 'file']
    }
}

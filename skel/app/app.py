import os
import logging
import pprint

from flask import Flask, g, url_for, request

from agg.jinja import register_jinja_filters
from agg.core import db, csrf

from common import INSTANCE_ROOT

from .log import AlchemyFormatter, FlaskFormatter


def create_app(cfg=None, purpose=None):
    """Application factory
    """
    app = Flask(__name__, instance_path=INSTANCE_ROOT)
    app.purpose = purpose
    load_config(app, cfg)

    init_logging(app)

    # Core components
    db.init_app(app)

    # initialize models
    with app.app_context():
        import agg.models

    csrf.init_app(app)

    register_blueprints(app)

    register_jinja_filters(app)

    log_all_requests(app)

    app.logger.info('Landlord {} загружен'.format(
        app.config['ENVIRONMENT'])
    )

    return app


def register_blueprints(app):
    from . import misc, users, services, feedback, payments, forums, bbs, files, news, faq, tariffs, nearby, admin

    # Модули, у которых определена функция __menu_item__(), будут следовать в меню в том же порядке, что и в этом списке
    modules = (misc, users, services, feedback, payments, forums, bbs, files, news, faq, tariffs, nearby, admin)

    for m in modules:
        app.register_blueprint(m.mod)


def init_logging(app):
    console_handler = logging.StreamHandler()

    if app.config['DEBUG']:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.ERROR)

    formatter = FlaskFormatter()
    console_handler.setFormatter(formatter)

    app.logger.handlers = []
    app.logger.propagate = False
    app.logger.addHandler(console_handler)

    db_logger_level = logging.INFO if app.config['SQLALCHEMY_TRUE_ECHO'] else logging.WARNING

    db_formatter = AlchemyFormatter()

    db_handler = logging.StreamHandler()
    db_handler.setFormatter(db_formatter)

    db_logger = logging.getLogger('sqlalchemy.engine')
    db_logger.propagate = False

    db_logger.addHandler(db_handler)
    logging.getLogger('sqlalchemy.engine').setLevel(db_logger_level)


def load_config(app, cfg=None):
    """Загружает в app конфиг из config.py, а потом обновляет его py-файла в cfg или, если он не указан, из переменной
    окружения BIGANTO_CFG
    """
    app.config.from_pyfile('config.py')

    if os.path.isfile('config.local.py'):
        app.config.from_pyfile('config.local.py')

    if cfg is None and 'LANDLORD_CFG' in os.environ:
        cfg = os.environ['LANDLORD_CFG']

    if cfg is not None:
        app.config.from_pyfile(cfg)


def log_all_requests(app):
    def post_data():
        if request.method == 'POST':
            return pprint.pformat(request.form.to_dict())
        return ''

    level = app.config.get('LOG_REQUESTS')
    if level:
        @app.before_request
        def log_all():
            if level == 1:
                app.logger.info('[{}] {}'.format(request.method, request.url))
            elif level == 2:
                app.logger.info('[{}] {}\n{}'.format(request.method, request.url, post_data()))

import os

from flask import Flask

from {{ name }}.jinja import register_jinja_filters
from {{ name }}.core import db, csrf
{% if 'SQLALCHEMY_LOGGING' in core -%}
from .log import init_logging
{%- endif %}

def create_app(cfg=None, purpose=None):
    """Application factory
    """
    app = Flask(__name__)
    app.purpose = purpose
    load_config(app, cfg)

    {% if 'SQLALCHEMY_LOGGING' in core -%}
    init_logging(app)
    {%- endif %}

    # Core components
    db.init_app(app)

    # Initialize models
    with app.app_context():
        import {{ name }}.models

    csrf.init_app(app)

    {% if 'FLASK_LOGIN' in core -%}
    init_login(app)
    {%- endif %}

    register_blueprints(app)

    register_jinja_filters(app)

    app.logger.info('{{ name }} %s загружен' % app.config['ENVIRONMENT'])

    return app


def register_blueprints(app):
    from . import {{ ', '.join(blueprints) }}

    modules = ({{ ', '.join(blueprints) }},)

    for m in modules:
        app.register_blueprint(m.mod)


def load_config(app, cfg=None):
    """Загружает в app конфиг из config.py, а потом обновляет его py-файла в cfg или, если он не указан, из переменной
    окружения {{ name|upper }}_CFG
    """
    app.config.from_pyfile('config.py')

    if os.path.isfile('config.local.py'):
        app.config.from_pyfile('config.local.py')

    if cfg is None and '{{ name|upper }}_CFG' in os.environ:
        cfg = os.environ['{{ name|upper }}_CFG']

    if cfg is not None:
        app.config.from_pyfile(cfg)

{% if 'FLASK_LOGIN' in core -%}
def init_login(app):
    from .core import login_manager
    from {{ name }}.models import User
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
{%- endif %}
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
{% if 'FLASK_LOGIN' in core -%}
from flask_login import LoginManager
{%- endif %}

db = SQLAlchemy()

csrf = CsrfProtect()

{% if 'FLASK_LOGIN' in core -%}
login_manager = LoginManager()
{%- endif %}

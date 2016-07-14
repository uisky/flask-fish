from flask import Blueprint

mod = Blueprint('{{ blueprint }}', __name__, url_prefix='/{{ blueprint }}')

from . import views

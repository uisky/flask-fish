import logging
import pprint

from flask import current_app
from flask.ext.script import Command

from {{ name }}.models import *


log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


class Example(Command):
    def run(self):
        print('Эта хреновина ничего не делает.')
        pprint(current_app.config)

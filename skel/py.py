#!/usr/bin/env python

from flask.ext.script import Manager, Server

from {{ app }} import create_app
from manage import *


app = create_app('config.local.py')
manager = Manager(app)

manager.add_command("runserver", Server(port=5001))
# manager.add_command('example', Example())


if __name__ == "__main__":
    manager.run()

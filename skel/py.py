#!/usr/bin/env python

from flask_script import Manager, Server

from {{ name }} import create_app
from manage import *


app = create_app('config.local.py')
manager = Manager(app)

manager.add_command("runserver", Server(port={{ serverport }}))
# manager.add_command('example', Example())


if __name__ == "__main__":
    manager.run()

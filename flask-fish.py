import argparse
import npyscreen
import random
import string
import os
import jinja2
from collections import OrderedDict

CORE_MODULES = OrderedDict([
    ('ALEMBIC', 'alembic'),
    ('SQLALCHEMY', 'sqlalchemy'),
    ('FLASK_SCRIPT', 'flask-script'),
    ('FLASK_LOGIN', 'flask-login (implies users blueprint)'),
    ('SQLALCHEMY_LOGGING', 'sqlalchemy logging'),
])

TEMPLATE_BOOTSTRAP3 = 0
TEMPLATE_YANDEX_MAPS = 1
TEMPLATE_GOOGLE_MAPS = 2


def random_string(length):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])


class FishApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm('MAIN', ConfigForm())


class ConfigForm(npyscreen.ActionForm):
    def create(self):
        self.wg = {}
        self.wg['name'] = self.add(npyscreen.TitleText, name="Package name:", value=options['name'])
        self.wg['dst_dir'] = self.add(
            npyscreen.TitleFilenameCombo, name="Directory:", select_dir=True, must_exist=False,
            confirm_if_exists=True, value=options['dst_dir']
        )
        self.wg['serverport'] = self.add(npyscreen.TitleText, name="Server port:", value=options['serverport'])

        core_modules = list(CORE_MODULES.values())
        self.wg['core'] = self.add(
            npyscreen.TitleMultiSelect, max_height=len(core_modules) + 1, value=options['core'], name="Core:",
            values=core_modules, scroll_exit=True
        )

        self.wg['blueprints'] = self.add(npyscreen.TitleText, name='Blueprints', value='front, admin')

        # self.wg['template'] = self.add(
        #     npyscreen.TitleMultiSelect, max_height=4, value=options['template'], name="Template:",
        #     values=['bootstrap 3.0', 'Яндекс.Карты', 'Google Maps'], scroll_exit=True
        # )

        self.wg['dbname'] = self.add(npyscreen.TitleText, name="DB name:", value=options['dbname'])
        self.wg['dbuser'] = self.add(npyscreen.TitleText, name="DB user:", value=options['dbuser'])
        self.wg['dbpass'] = self.add(npyscreen.TitleText, name="DB password:", value=options['dbpass'])
        self.wg['dbcreate'] = self.add(npyscreen.Checkbox, name="Create DB (issues sudo -u postgres psql -c ...)", value=True)

    def afterEditing(self):
        self.parentApp.setNextForm(None)

    def on_ok(self):
        for k, wg in self.wg.items():
            options[k] = wg.value

        options['dst_dir'] = os.path.abspath(options['dst_dir'])
        options['blueprints'] = [x.strip() for x in options['blueprints'].split(',') if x.strip() != '']

        core = []
        for i in options['core']:
            core.append(list(CORE_MODULES.items())[i][0])
        options['core'] = core

    def on_cancel(self):
        exit()


def copy_file(src, dst=None, **kwargs):
    if dst is None:
        dst = os.path.join(options['dst_dir'], src)
    print('%s -> %s' % (src, dst))
    template = jenv.get_template(src)

    o = options.copy()
    o.update(kwargs)

    with open(dst, 'w') as fh:
        fh.write(template.render(**o))


def create_project():
    print('Creating project %s in dir %s' % (options['name'], options['dst_dir']))
    from pprint import pprint

    if os.path.exists(options['dst_dir']):
        print('WARNING: Directory exists')

    # Ядро
    app_dir = os.path.join(options['dst_dir'], options['name'])
    os.makedirs(options['dst_dir'], exist_ok=True)
    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(os.path.join(app_dir, 'static'), exist_ok=True)
    os.makedirs(os.path.join(app_dir, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(app_dir, 'models'), exist_ok=True)

    for file in ('.gitignore', 'uwsgi.py', 'requirements.txt'):
        copy_file(file)

    for file in ('config.py', 'config.local.py', '__init__.py', 'app.py', 'core.py', 'jinja.py', 'util.py',
                 'templates/base.html', 'static/common.js', 'static/common.css'):
        copy_file(os.path.join('app', file), os.path.join(app_dir, file))

    # blueprints
    for blueprint in options['blueprints']:
        bp_dir = os.path.join(app_dir, blueprint)
        os.makedirs(bp_dir, exist_ok=True)
        for file in ('__init__.py', 'views.py', 'forms.py'):
            copy_file(os.path.join('app/blueprint', file), os.path.join(bp_dir, file), blueprint=blueprint)

        # template
        os.makedirs(os.path.join(app_dir, 'templates', blueprint), exist_ok=True)
        copy_file(
            'app/templates/blueprint/index.html',
            os.path.join(app_dir, 'templates', blueprint, 'index.html'),
            blueprint=blueprint
        )

    # alembic
    if 'ALEMBIC' in options['core']:
        os.makedirs(os.path.join(options['dst_dir'], 'alembic', 'versions'), exist_ok=True)
        for file in ('alembic.ini', 'alembic/env.py', 'alembic/script.py.mako'):
            copy_file(file)

    # flask_script
    if 'FLASK_SCRIPT' in options['core']:
        os.makedirs(os.path.join(options['dst_dir'], 'manage'), exist_ok=True)
        copy_file('py.py')
        copy_file('manage/__init__.py')
        copy_file('manage/example.py')
    else:
        copy_file('entry.py')

    if 'FLASK_LOGIN' in options['core']:
        pass

    if 'SQLALCHEMY_LOGGING' in options['core']:
        copy_file(os.path.join('app', 'log.py'), os.path.join(app_dir, 'log.py'))

    if options['dbcreate']:
        os.system(""" sudo -u postgres psql -c "CREATE USER {dbuser} ENCRYPTED PASSWORD '{dbpass}'" """.format(**options))
        os.system(""" sudo -u postgres psql -c "CREATE DATABASE {dbname} OWNER {dbuser}" """.format(**options))

if __name__ == "__main__":
    ap = argparse.ArgumentParser('flask-fish', add_help=True)
    ap.add_argument('name', help='Package name', nargs='?')
    ap.add_argument('dst_dir', help='Project directory', nargs='?')
    cmdline = ap.parse_args()

    options = {
        'name': cmdline.name,
        'dst_dir': cmdline.dst_dir,
        'serverport': '5000',
        'core': [0, 1, 2],
        'template': [0],
        'dbname': cmdline.name,
        'dbuser': cmdline.name,
        'dbpass': random_string(12)
    }
    if options['dst_dir'] is None:
        options['dst_dir'] = options['name']

    App = FishApp()
    App.run()

    skel_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'skel')
    jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(skel_dir))

    create_project()

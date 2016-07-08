import argparse
import npyscreen
import random
import string
import os
import jinja2


CORE_ALEMBIC = 0
CORE_SQLALCHEMY = 1
CORE_FLASK_SCRIPT = 2
CORE_FLASK_LOGIN = 3

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
        self.wg['dst_dir'] = self.add(
            npyscreen.TitleFilenameCombo, name="Directory:", select_dir=True, must_exist=False,
            confirm_if_exists=True, value=options['dst_dir']
        )
        self.wg['name'] = self.add(npyscreen.TitleText, name="Package name:", value=options['name'])

        self.wg['core'] = self.add(
            npyscreen.TitleMultiSelect, max_height=5, value=options['core'], name="Core:",
            values=['alembic', 'sqlalchemy', 'flask-script', 'flask-login'], scroll_exit=True
        )

        self.wg['template'] = self.add(
            npyscreen.TitleMultiSelect, max_height=4, value=options['template'], name="Template:",
            values=['bootstrap 3.0', 'Яндекс.Карты', 'Google Maps'], scroll_exit=True
        )

        self.wg['dbname'] = self.add(npyscreen.TitleText, name="DB name:", value=options['dbname'])
        self.wg['dbuser'] = self.add(npyscreen.TitleText, name="DB user:", value=options['dbuser'])
        self.wg['dbpass'] = self.add(npyscreen.TitleText, name="DB password:", value=options['dbpass'])

    def afterEditing(self):
        self.parentApp.setNextForm(None)

    def on_ok(self):
        for k, wg in self.wg.items():
            options[k] = wg.value

    def on_cancel(self):
        exit()


def copy_file(src):
    dst = os.path.join(options['dst_dir'], src)
    print('Copy %s to %s' % (src, dst))
    template = jenv.get_template(src)
    with open(dst, 'w') as fh:
        fh.write(template.render(**options))


def create_project():
    options['dst_dir'] = os.path.abspath(options['dst_dir'])

    print('Creating project %s in dir %s' % (options['name'], options['dst_dir']))
    if os.path.exists(options['dst_dir']):
        print('WARNING: Directory exists')

    # Ядро
    os.makedirs(options['dst_dir'], exist_ok=True)
    os.makedirs(os.path.join(options['dst_dir'], options['name']), exist_ok=True)
    for file in ('.gitignore', 'uwsgi.py', 'requirements.txt'):
        copy_file(file)

    if CORE_ALEMBIC in options['core']:
        os.makedirs(os.path.join(options['dst_dir'], 'alembic'), exist_ok=True)

    if CORE_FLASK_SCRIPT in options['core']:
        os.makedirs(os.path.join(options['dst_dir'], 'manage'), exist_ok=True)
        copy_file('py.py')
        copy_file('manage/__init__.py')
        copy_file('manage/example.py')
    else:
        copy_file('entry.py')

if __name__ == "__main__":
    ap = argparse.ArgumentParser('flask-fish', add_help=True)
    ap.add_argument('dst_dir', help='Project directory', nargs='?')
    ap.add_argument('name', help='Package name', nargs='?')
    cmdline = ap.parse_args()

    options = {
        'name': cmdline.name,
        'dst_dir': cmdline.dst_dir,
        'core': [0, 1],
        'template': [0],
        'dbname': cmdline.name,
        'dbuser': cmdline.name,
        'dbpass': random_string(12)
    }

    App = FishApp()
    App.run()

    skel_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'skel')
    jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(skel_dir))

    create_project()

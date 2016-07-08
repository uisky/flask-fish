import math

from collections import OrderedDict
import phonenumbers
from wtforms import Form, StringField, IntegerField, SelectMultipleField
from wtforms.widgets import FileInput, ListWidget, CheckboxInput

from flask import flash, render_template, current_app, abort
from flask import current_app as app


def flash_errors(form):
    """
    Перетаскивает ошибки из WTF-формы form в flash(..., 'error')
    :param form: Form
    :return:
    """
    for field, errors in form.errors.items():
        for error in errors:
            if app.config['DEBUG']:
                text = '{}: {}'.format(field, error)
                flash(text, 'danger')
                print(text)
            else:
                flash(error, 'danger')


def plural(x, var1, var2, var5):
    """
    Спряжение существительных после числительного. Например:
    У вас в штанах {{ x }} {{ x|plural('енотик', 'енотика', 'енотиков') }}
    :param x: количество
    :param var1: 1, 21, 31, ...
    :param var2: 2-4, 22-24, 33-34, ...
    :param var5: 0, 5-9, 10-20, 25-30, 35-40, ...
    :return:
    """
    x = abs(x)
    if x == 0:
        return var5
    if x % 10 == 1 and x % 100 != 11:
        return var1
    elif 2 <= (x % 10) <= 4 and (x % 100 < 10 or x % 100 >= 20):
        return var2
    else:
        return var5


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


def copy_row(row, ignored_columns=('id', 'created')):
    model = row.__class__
    copy = model()

    for col in row.__table__.columns:
        if col.name not in ignored_columns:
            setattr(copy, col.name, getattr(row, col.name))

    return copy


# from http://flask.pocoo.org/docs/0.10/patterns/viewdecorators/#templating-decorator

from functools import wraps
from flask import request

def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator


def get_app():
    return app._get_current_object()


class DbDict:
    def __init__(self, model):
        self.model = model
        self.data = None

    def reload(self):
        self.data = {row.id: row for row in self.model.query.all()}

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, item):
        return item in self.data

    def to_dict(self):
        return self.data


def group(seq, by=(lambda x: (x, x, x)), items_as='dict'):
    """
    Операция group by по последовательности
    seq - Исходная последовательность. Должна быть заранее отсортирована так, чтобы
          элементы в пределах одной группы шли подряд. Исходный порядок сортировки
          будет сохранён также и для элементов внутри групп, если items_as='list'.
    by  - Функция, которая будет применяться к элементам последовательности. 
          Для каждого элемента выдает кортеж вида: (group_key, item_key, item_value)
    items_as - 'dict' или 'list'. В чём сохранять элементы внутри группы.
            dict - в OrderedDict. item_key используется как ключ словаря
            list - в список.

    Возвращает OrderedDict    
    """
    d = OrderedDict()

    for group_key, item_key, item_value in (by(i) for i in seq):
        if group_key not in d:
            if items_as == 'dict':
                d[group_key] = OrderedDict({item_key: item_value})
            elif items_as == 'list':
                d[group_key] = [item_value]
        else:
            if items_as == 'dict':
                d[group_key][item_key] = item_value
            elif items_as == 'list':
                d[group_key].append(item_value)

    return d


def test_endpoint(fn):
    def f(*args, **kwargs):
        if app.config['ENVIRONMENT'] == 'production':
            abort(403)
        else:
            return fn(*args, **kwargs)
    return f


def dump_obj(obj, title=''):
    if title is not None:
        print('\033[31m%s\033[0m' % title)
    for x in dir(obj):
        print('    \033[32m%s\033[0m: %s' % (x, type(getattr(obj, x))))


metric_prefix = {
    -24: 'йокто',
    -21: 'зепто',
    -18: 'атто',
    -15: 'фемто',
    -12: 'пико',
    -9: 'нано',
    -6: 'микро',
    -3: 'милли',
    0: '',
    3: 'кило',
    6: 'мега',
    9: 'гига',
    12: 'тера',
    15: 'пета',
    18: 'экза',
    21: 'зетта',
    24: 'йотта'
}

metric_prefix_short = {
    -24: 'и',
    -21: 'з',
    -18: 'а',
    -15: 'ф',
    -12: 'п',
    -9: 'н',
    -6: 'мк',
    -3: 'м',
    0: '',
    3: 'К',
    6: 'М',
    9: 'Г',
    12: 'Т',
    15: 'П',
    18: 'Э',
    21: 'З',
    24: 'И'
}

ending = {
    0: '',
    1: '',
    2: 'а',
    3: 'а',
    4: 'а',
    5: '',
    6: '',
    7: '',
    8: '',
    9: ''
}


def order(x):
    return int(math.log10(x) / 3) * 3


def human_file_size(x, variant='long'):
    if x < 0:
        return 'отрицательный размер'
    elif x == 0:
        return '0 байт' if variant == 'long' else '0'
    elif x < 1.616229383838e-35:
        return 'размер меньше планковского... проверьте расчёты, коллега'
    elif x < 1:
        bits = int(x * 8)
        return '{} бит{}'.format(bits, ending[bits])
    elif x > 1e24:
        return '%.3e байт' % x
    elif x > 1e81:
        return 'размер превышает число атомов во Вселенной'
    else:
        number = round(x / (10 ** order(x)), 1)
        if number == int(number):
            number = int(number)
        if number > 10:
            number = int(number)
        if variant == 'long':
            return '{} {}байт{}'.format(number, metric_prefix[order(x)], ending.get(number % 10, ''))
        else:
            return '{} {}б'.format(number, metric_prefix_short[order(x)])

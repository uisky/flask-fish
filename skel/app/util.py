import math

from flask import flash, render_template, abort
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
                error = '{}: {}'.format(field, error)
            flash(error, 'danger')


def plural(x, var1, var2, var5):
    {%- raw %}
    """
    Спряжение существительных после числительного. Например:
    У вас в штанах {{ x }} {{ x|plural('енотик', 'енотика', 'енотиков') }}
    :param x: количество
    :param var1: 1, 21, 31, ...
    :param var2: 2-4, 22-24, 33-34, ...
    :param var5: 0, 5-9, 10-20, 25-30, 35-40, ...
    :return:
    """
    {% endraw -%}
    x = abs(x)
    if x == 0:
        return var5
    if x % 10 == 1 and x % 100 != 11:
        return var1
    elif 2 <= (x % 10) <= 4 and (x % 100 < 10 or x % 100 >= 20):
        return var2
    else:
        return var5


def copy_row(row, ignored_columns=('id', 'created')):
    model = row.__class__
    copy = model()

    for col in row.__table__.columns:
        if col.name not in ignored_columns:
            setattr(copy, col.name, getattr(row, col.name))

    return copy


def test_endpoint(fn):
    """
    Запрещает эндпоинту работать в продакшене
    :param fn:
    :return:
    """
    def f(*args, **kwargs):
        if app.config['ENVIRONMENT'] == 'production':
            abort(403)
        else:
            return fn(*args, **kwargs)
    return f


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
        return '{} бит{}'.format(bits, plural(bits, 'бит', 'бита', 'бит'))
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
            return '{} {}{}'.format(number, metric_prefix[order(x)], plural(number, 'байт', 'байта', 'байт'))
        else:
            return '{} {}б'.format(number, metric_prefix_short[order(x)])

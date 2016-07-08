from flask import get_flashed_messages
import common
from urllib.parse import urlsplit
from agg import util


def register_jinja_filters(app):
    @app.context_processor
    def flashes():
        """
        Возвращает flash-сообщения в виде [('error', [msg1, msg2, msg3]), ('success', [msg1, msg2]), ...]
        :return:
        """
        def make_flashes():
            result = {}
            for cat, msg in get_flashed_messages(with_categories=True):
                result.setdefault(cat, []).append(msg)
            return result

        return {'flashes': make_flashes}

    @app.template_filter('plural')
    def jinja_plural(x, var1, var2, var5):
        return util.plural(x, var1, var2, var5)

    @app.template_filter('humantime')
    def humantime(ts):
        now = common.now()
        if now.year == ts.year:
            if now.month == ts.month:
                if now.day == ts.day:
                    return ts.strftime('сегодня в %H:%M')
                elif (now - ts).days == 1:
                    return ts.strftime('вчера в %H:%M')
            return ts.strftime('%d.%m %H:%M')
        return ts.strftime('%d.%m.%Y %H:%M')

    @app.template_filter('money')
    def jinja_money(x):
        if x is None:
            return '0'
        return '{:,}'.format(round(x)).replace(',', ' ')

    months = {
        1: 'Январь',
        2: 'Февраль',
        3: 'Март',
        4: 'Апрель',
        5: 'Май',
        6: 'Июнь',
        7: 'Июль',
        8: 'Август',
        9: 'Сентябрь',
        10: 'Октябрь',
        11: 'Ноябрь',
        12: 'Декабрь'
    }

    @app.template_filter('month')
    def month(x):
        return months[x]

    @app.template_filter('ellipsis')
    def ellipsis(x, length):
        return x[:length].rsplit(' ', 1)[0] + '...' if len(x) > length else x


import pytz
from datetime import datetime

from flask import get_flashed_messages, Markup
from {{ name }} import util


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
        now = pytz.utc.localize(datetime.now())
        if now.year == ts.year:
            if now.month == ts.month:
                if now.day == ts.day:
                    return ts.strftime('сегодня в %H:%M')
                elif (now - ts).days == 1:
                    return ts.strftime('вчера в %H:%M')
            return ts.strftime('%d.%m %H:%M')
        return ts.strftime('%d.%m.%Y %H:%M')

    @app.template_filter('nl2br')
    def nl2br(t):
        if isinstance(t, str):
            t = str(Markup.escape(t))
            t = t.strip().replace('\r', '').replace('\n', '<br>')
        return Markup(t)

    @app.template_filter('money')
    def jinja_money(x):
        if x is None:
            return '0'
        return '{:,}'.format(round(x)).replace(',', ' ')

    @app.template_filter('ellipsis')
    def ellipsis(x, length):
        return x[:length].rsplit(' ', 1)[0] + '...' if len(x) > length else x


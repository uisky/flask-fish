import logging
import pprint
import sqlparse
import re
import ast
import datetime
from functools import partial

from common import color


class FlaskFormatter(logging.Formatter):
    format_string = ('%(levelname)s ' + color.black('%(asctime)s %(pathname)s:%(lineno)d\n') +
                     '%(message)s\n')

    def format(self, record):
        level_color = {
            'DEBUG': partial(color.cyan, style='bold'),
            'INFO': partial(color.white, dark=True, style='bold'),
            'WARNING': partial(color.yellow, style='bold'),
            'ERROR': partial(color.red, style='bold'),
            'CRITICAL': partial(color.red, background=True, style='bold')
        }
        record.levelname = level_color[record.levelname](record.levelname)
        record.message = record.getMessage()
        record.asctime = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return self.format_string % record.__dict__


class AlchemyFormatter(FlaskFormatter):
    def format(self, record):
        record.asctime = self.formatTime(record)
        _message = record.msg % record.args if record.args else record.msg
        record.args = None
        if _message[:1] == '{':
            params = ast.literal_eval(_message)
            record.msg = '\033[34m{}\033[0m'.format(pprint.pformat(params, indent=4))
        else:
            keywords = (
                'SELECT', 'FROM', 'LEFT', 'RIGHT', 'INNER', 'UNION', 'ALL', 'JOIN', 'GROUP', 'BY',
                'HAVING', 'INSERT', 'UPDATE', 'DELETE', 'VALUES', 'COMMIT', 'ROLLBACK',
                'LIMIT', 'OFFSET', 'WHERE', 'OUTER', 'CAST', 'ORDER', ' AS ', ' ON '
            )
            rep = {re.escape(k): '\033[1;32m{}\033[0;32m'.format(k) for k in keywords}
            pattern = re.compile('|'.join(rep.keys()))
            _message = pattern.sub(lambda m: rep[re.escape(m.group(0))],
                                   sqlparse.format(_message, reindent=True, keyword_case='upper'))
            record.msg = '\033[32m{}\033[0m'.format(_message)
        return super().format(record)

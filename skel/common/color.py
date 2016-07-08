colors = {
    'black':   '0',
    'red':     '1',
    'green':   '2',
    'yellow':  '3',
    'blue':    '4',
    'magenta': '5',
    'cyan':    '6',
    'white':   '7'
}

DROP_COLOR = '\033[0m'

def _mod1(dark, background):
    return {
        (False, False): '9',
        (False, True):  '10',
        (True, False):  '3',
        (True, True):   '4'
    }[(dark, background)]

def _mod2(style):
    return {
        'bold': ';1',
        'underline': ';4',
        '': ''
    }[style]


def _color(s, color, dark, background, style):
    return '\033[{}{}{}m{}\033[0m'.format(_mod1(dark, background), colors[color], _mod2(style), str(s))


def black(s, dark=False, background=False, style=''):
    return _color(s, 'black', dark, background, style)

def red(s, dark=False, background=False, style=''):
    return _color(s, 'red', dark, background, style)

def green(s, dark=False, background=False, style=''):
    return _color(s, 'green', dark, background, style)

def yellow(s, dark=False, background=False, style=''):
    return _color(s, 'yellow', dark, background, style)

def blue(s, dark=False, background=False, style=''):
    return _color(s, 'blue', dark, background, style)

def magenta(s, dark=False, background=False, style=''):
    return _color(s, 'magenta', dark, background, style)

def cyan(s, dark=False, background=False, style=''):
    return _color(s, 'cyan', dark, background, style)

def white(s, dark=False, background=False, style=''):
    return _color(s, 'white', dark, background, style)

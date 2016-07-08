# -*- coding: utf-8 -*-
import os
import pytz
import datetime

INSTANCE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self    


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


def is_iterable_but_not_string(obj):
    return getattr(obj, '__iter__', False) and not isinstance(obj, str)


def homogeneous_type(objects, class_):
    '''
    Являются ли элементы objects экземплярами одного класса?
    '''
    return all((isinstance(obj, class_) for obj in objects))


def import_local_module(name, filename):
    '''
    Импорт модуля из файла filename с именем name
    filename - путь относительно корня проекта
    '''
    try:
        # python 3
        import importlib.machinery
        loader = importlib.machinery.SourceFileLoader(name, os.path.join(INSTANCE_ROOT, filename))
        module = loader.load_module()
    except:
        # python 2
        import imp
        module = imp.load_source(name, os.path.join(INSTANCE_ROOT, filename))

    return module


def now():
    return pytz.utc.localize(datetime.datetime.utcnow())


def dt_round(dt, unit):
    if unit == 'hour':
        return datetime.datetime(dt.year, dt.month, dt.day, dt.hour, tzinfo=dt.tzinfo)
    elif unit == 'day':
        return datetime.datetime(dt.year, dt.month, dt.day, tzinfo=dt.tzinfo)
    elif unit == 'month':
        return datetime.datetime(dt.year, dt.month, 1, tzinfo=dt.tzinfo)
    else:
        raise ValueError('Не знаю как округлять до %s' % str(unit))


def get_extension(path):
    s = path.rsplit('.', 1)
    if len(s) == 1:
        # no extension
        return ''
    else:
        return '.' + s[-1]

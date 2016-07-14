from flask import render_template, abort, request, flash, redirect, url_for

from . import mod
from ..models import *


@mod.route('/')
def index():
    return render_template('{{ blueprint }}/index.html')

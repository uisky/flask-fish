import uuid

from flask import render_template, request, redirect, flash, url_for, jsonify, abort
from flask_login import login_user, logout_user, login_required

from {{ name }}.core import db, csrf
from {{ name }}.mail import send_email
from {{ name }}.util import flash_errors
from {{ name }}.models import User
from . import mod, forms


@mod.route('/')
def index():
    abort(501)


@mod.route('/login/', methods=('POST',))
@csrf.exempt
def login():
    is_ajax = request.args.get('ajax')

    def success():
        if is_ajax:
            return jsonify(status='ok')
        else:
            return redirect(request.args.get('next', '/'))

    def fail(error):
        if is_ajax:
            return jsonify(status='error', errors=[error])
        else:
            flash(error, 'danger')
            return redirect(url_for('front.index'))

    user = User.query.filter(User.email == request.form.get('email')).first()

    if user and User.hash_password(request.form.get('password', '')) == user.password_hash:
        if not login_user(user, remember=True):
            return fail('Пароль верный, но ваш аккаунт не активен.')
    else:
        return fail('Неправильный e-mail или пароль.')

    return success()


@mod.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect('/')


@mod.route('/register/', methods=('GET', 'POST'))
def register():
    def check():
        email_exists = User.query.filter(db.func.lower(User.email) == form.email.data.lower()).first()
        if email_exists:
            flash('Пользователь с такой электронной почтой уже зарегистрирован.', 'danger')
            return False
        return True

    user = User()
    form = forms.RegisterForm(obj=user)

    if form.validate_on_submit() and check():
        if form.password.data != form.password2.data:
            flash('Введённые пароли не совпадают.')
        else:
            user.email = form.email.data
            user.name = form.name.data
            user.password_hash = User.hash_password(form.password.data)
            user.roles = 0

            db.session.add(user)
            db.session.commit()

            return render_template('users/after_register.html', email=user.email)

    flash_errors(form)

    return render_template('users/register.html', form=form)


@mod.route('/remind/', methods=('GET', 'POST'))
def remind():
    form = forms.RemindPasswordForm(request.form)
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter(db.func.lower(User.email) == email).first()
        if not user:
            flash('Пользователь с таким email не зарегистрирован', 'danger')
        else:
            token = uuid.uuid4().hex
            redis.set('remind-token:{}'.format(token), user.id, 60 * 60 * 24)
            restore_url = url_for('.restore_password', user_id=user.id, token=token,
                                       _external=True)
            send_email(
                template='users/email/restore_password',
                subject='Восстановление пароля',
                recipients=[user.email],
                restore_url=restore_url
            )

            return render_template('users/after_remind.html', email=user.email)

    return render_template('users/remind.html', form=form)


@mod.route('/restore-password/', methods=('GET', 'POST'))
def restore_password():
    user_id = request.args.get('user_id')
    token = request.args.get('token')
    key = 'remind-token:{}'.format(token)
    if not user_id:
        flash('Ссылка для восстановления пароля неправильная или устарела', 'danger')
        return redirect(url_for('misc.index'))

    user = User.query.get_or_404(user_id)
    form = forms.RestorePasswordForm()

    if int(redis.get(key) or 0) != user.id:
        flash('Ссылка для восстановления пароля неправильная или устарела', 'danger')
        return redirect(url_for('misc.index'))

    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            flash('Введённые пароли не совпадают', 'danger')
        else:
            user.password_hash = User.hash_password(form.password.data)
            db.session.commit()
            redis.delete(key)
            return redirect(url_for('misc.index'))

    return render_template('/users/restore_password.html', form=form, user=user)

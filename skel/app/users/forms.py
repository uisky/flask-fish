from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms import validators as v


class RegisterForm(Form):
    email = StringField('E-mail', [
        v.required(message='Введите e-mail'),
        v.Email(message='Неправильный адрес электронной почты')
    ])
    password = PasswordField('Пароль', [v.required(message='Введите пароль.')])
    password2 = PasswordField('Пароль ещё раз', [v.required(message='Введите пароль ещё раз')])
    name = StringField('Ник', [v.required(message='Введите ник')])


class SettingsForm(Form):
    password = StringField('Пароль', [v.optional()])


class RemindPasswordForm(Form):
    email = StringField('E-mail', [v.required('Пожалуйста, введите e-mail')])


class RestorePasswordForm(Form):
    password = PasswordField('Пароль', [v.required(message='Введите пароль.')])
    password2 = PasswordField('Пароль ещё раз', [v.required(message='Введите пароль ещё раз')])

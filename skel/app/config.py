DEBUG = False

ENVIRONMENT = 'production'

SERVER_NAME = '{{ name }}.ru'

SQLALCHEMY_DATABASE_URI = 'postgresql://{{ dbuser }}:{{ dbpass }}@localhost:5432/{{ dbname }}'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'override-this!'

# WTF_CSRF_CHECK_DEFAULT = False
# WTF_CSRF_ENABLED = False

MAIL_ENABLED = True
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_DEFAULT_SENDER = 'no-reply@{{ name }}.ru'



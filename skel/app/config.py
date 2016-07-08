DEBUG = False

ENVIRONMENT = 'production'

SERVER_NAME = 'agg.biganto.ru'

SQLALCHEMY_DATABASE_URI = 'postgresql://agg:agg@localhost:5432/landlord'
SQLALCHEMY_TRUE_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'override-this!'

# WTF_CSRF_CHECK_DEFAULT = False
# WTF_CSRF_ENABLED = False

MAIL_ENABLED = True
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
# MAIL_USE_TLS = False
# MAIL_USE_SSL = False
# MAIL_DEBUG = DEBUG
# MAIL_USERNAME = ''
# MAIL_PASSWORD = ''
# MAIL_DEFAULT_SENDER = 'noreply@landlord.ru'



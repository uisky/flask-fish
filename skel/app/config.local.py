DEBUG = True

ENVIRONMENT = 'local'

SERVER_NAME = '{{ name }}.dev.romakhin.ru'

SQLALCHEMY_DATABASE_URI = 'postgresql://{{ dbuser }}:{{ dbpass }}@localhost:5432/{{ dbname }}'
SQLALCHEMY_ECHO = True

MAIL_DEBUG = True

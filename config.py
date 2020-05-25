import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	MAIL_SERVER = os.environ.get('MAIL_SERVER')
	MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

	MAIL_DEFAULT_SENDER = ('SmartClinic', os.getenv('MAIL_USERNAME'))
	# MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

	UNITS_PER_PAGE = 10
	UNITS_PER_PAGE_ADD = 3
	RECORDS_PER_PAGE = 10
	RECORDS_PER_PAGE_ADD = 3
	EVALUATIONS_PER_PAGE_ADD = 10

	WHOOSHEE_MIN_STRING_LEN = 1

	ADMIN_EMAIL = "zirui.liu@pku.edu.cn"

	# AVATARS_SAVE_PATH = '/root/compNet/app/static/images/avatars'
	AVATARS_SAVE_PATH = '/root/compNet/app/static/images/avatars'

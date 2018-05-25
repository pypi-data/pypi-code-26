# -*- coding: utf-8 -*-

import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import Model
from flask_wtf.csrf import CSRFProtect
from raven.contrib.flask import Sentry
from raven.contrib.celery import register_logger_signal, register_signal
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, Integer

from pipet.utils.celery import make_celery


class Base(Model):
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, server_default=func.now(), nullable=False)


load_dotenv()
csrf = CSRFProtect()
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
sentry = Sentry(logging=True, level=logging.ERROR, wrap_wsgi=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'POSTGRES_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME', None)
app.config['PREFERRED_URL_SCHEME'] = os.environ.get('PREFERRED_URL_SCHEME')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL')
app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL')
app.config['GOOGLE_PICKER_API_KEY'] = os.environ.get('GOOGLE_PICKER_API_KEY')
app.config['WEBPACK_MANIFEST_PATH'] = 'static/build/manifest.json'
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

csrf.init_app(app)
db.init_app(app)
sentry.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'index'

celery = make_celery(app)
celery.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': os.environ.get('REDIS_URL'),
        'default_timeout': 60 * 60,
    }
}

from pipet.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


from pipet import views  # NOQA
from pipet import cli  # NOQA

# from pipet.api.views import blueprint as api_blueprint

# app.register_blueprint(api_blueprint, url_prefix='/api')

from pipet.sources.zendesk import ZendeskAccount
from pipet.sources.zendesk.views import blueprint as zendesk_blueprint

app.register_blueprint(zendesk_blueprint, url_prefix='/zendesk')

from pipet.sources.stripe import StripeAccount
from pipet.sources.stripe.views import blueprint as stripe_blueprint

app.register_blueprint(stripe_blueprint, url_prefix='/stripe')

from pipet.sources.zendesk.tasks import sync as sync_zendesk

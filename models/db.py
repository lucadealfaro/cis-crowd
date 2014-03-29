# -*- coding: utf-8 -*-

import urllib
from gluon.custom_import import track_changes; track_changes(True) # for reloading modules

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

db = DAL('google:datastore', adapter_args={'use_ndb':True})
## store sessions and tickets there
session.connect(request, response, db=db)
## or store session in Memcache, Redis, etc.
## from gluon.contrib.memdb import MEMDB
## from google.appengine.api.memcache import Client
## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

# Logging in via Google Accounts
from gluon.contrib.login_methods.gae_google_account import GaeGoogleAccount
auth.settings.login_form=GaeGoogleAccount()

# No logging of auth events.
auth.settings.logging_enabled = False

# Adds a timezone field to the auth table.
from pytz.gae import pytz
from plugin_timezone import tz_nice_detector_widget
my_tz_nice_detector_widget = lambda field, value : tz_nice_detector_widget(field, value, autodetect=True)
     
auth.settings.extra_fields['auth_user']= [
  Field('user_timezone', 'string', widget=my_tz_nice_detector_widget),
]

## create all tables needed by auth if not custom tables
auth.define_tables(username=False)

auth.settings.table_user.first_name.readable = auth.settings.table_user.first_name.writable = True
auth.settings.table_user.last_name.readable = auth.settings.table_user.last_name.writable = True
auth.settings.table_user.user_timezone.label = T('Time zone')

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

##### This tells web2py to use GAE logins.
if request.env.web2py_runtime_gae:
    from gluon.contrib.login_methods.gae_google_account import GaeGoogleAccount
    auth.settings.login_form = GaeGoogleAccount()
    auth.settings.actions_disabled.append('request_reset_password')
    auth.settings.actions_disabled.append('reset_password')
    auth.settings.actions_disabled.append('retrieve_password')
    auth.settings.actions_disabled.append('email_reset_password')
    auth.settings.actions_disabled.append('change_password')
    auth.settings.actions_disabled.append('retrieve_username')
    auth.settings.actions_disabled.append('verify_email')
    auth.settings.actions_disabled.append('register')
    # auth.settings.actions_disabled.append('profile')
    db.auth_user.email.writable = False

#### How to get an email address.
def get_user_email():
    """Note that this function always returns a lowercase email address."""
    if request.env.web2py_runtime_gae:
        from google.appengine.api import users as googleusers
        u = googleusers.get_current_user()
        if u is None:
            return None
        else:
            return u.email().lower()
    else:
        if auth.user is None:
            return None
        else:
            return auth.user.email.lower()
            
## How to get an original email address (with original capitalization).

def get_user_system_email():
    """Use this for sending emails."""
    if request.env.web2py_runtime_gae:
        from google.appengine.api import users as googleusers
        u = googleusers.get_current_user()
        if u is None:
            return None
        else:
            return u.email()
    else:
        if auth.user is None:
            return None
        else:
            return auth.user.email
        
## How to get a user id (Google user id, in production).

def get_user_id():
    """Note that this function always returns a lowercase email address."""
    if request.env.web2py_runtime_gae:
        from google.appengine.api import users as googleusers
        u = googleusers.get_current_user()
        if u is None:
            return None
        else:
            return u.user_id()
    else:
        if auth.user is None:
            return None
        else:
            return auth.user.email
        
# Stores these in the current object.
from gluon import current
current.user_email = get_user_email()
current.user_system_email = get_user_system_email()
current.user_id = get_user_id()

######################
# Logging
import logging, logging.handlers

class GAEHandler(logging.Handler):
    """
    Logging handler for GAE DataStore
    """
    def emit(self, record):

        from google.appengine.ext import db

        class Log(db.Model):
            name = db.StringProperty()
            level = db.StringProperty()
            module = db.StringProperty()
            func_name = db.StringProperty()
            line_no = db.IntegerProperty()
            thread = db.IntegerProperty()
            thread_name = db.StringProperty()
            process = db.IntegerProperty()
            message = db.StringProperty(multiline=True)
            args = db.StringProperty(multiline=True)
            date = db.DateTimeProperty(auto_now_add=True)

        log = Log()
        log.name = record.name
        log.level = record.levelname
        log.module = record.module
        log.func_name = record.funcName
        log.line_no = record.lineno
        log.thread = record.thread
        log.thread_name = record.threadName
        log.process = record.process
        log.message = record.msg
        log.args = str(record.args)
        log.put()

def get_configured_logger(name):
    logger = logging.getLogger(name)
    if (len(logger.handlers) == 0):
        # This logger has no handlers, so we can assume it hasn't yet been configured
        # (Configure logger)

        # Create default handler
        if request.env.web2py_runtime_gae:
            # Create GAEHandler
            handler = GAEHandler()
            handler.setLevel(logging.WARNING)
            logger.addHandler(handler)
            logger.setLevel(logging.WARNING)
        else:
            # Create RotatingFileHandler
            import os
            formatter="%(asctime)s %(levelname)s %(process)s %(thread)s %(funcName)s():%(lineno)d %(message)s"
            handler = logging.handlers.RotatingFileHandler(os.path.join(request.folder,'private/app.log'),maxBytes=1024,backupCount=2)
            handler.setFormatter(logging.Formatter(formatter))
            handler.setLevel(logging.DEBUG)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

        # Test entry:
        # logger.debug(name + ' logger created')
    else:
        pass
        # Test entry:
        # logger.debug(name + ' already exists')

    return logger

# Assign application logger to a global var  
logger = get_configured_logger(request.application)

# Assign application logger to a global var
if request.env.web2py_runtime_gae:
    logger = logging
else:
    logger = get_configured_logger(request.application)

# Makes the db and logger available also to modules.
current.db = db
current.logger = logger

# Let's log the user. 
logger.info("User: %r Email: %r Id: %r" % 
            (current.user_email, current.user_system_email, current.user_id))

request_scheme = 'http'
if request.is_https:
    request_scheme = 'https'
request_host = request_scheme + '://' + request.env.http_host
logger.info("Request host: %r" % request_host)
current.request_host = request_host


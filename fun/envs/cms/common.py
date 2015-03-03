# -*- coding: utf-8 -*-

import sys

# import cms aws settings
from cms.envs.aws import *  # pylint: disable=wildcard-import, unused-wildcard-import
# import FUN lms/cms common settings
from ..common import *


INSTALLED_APPS += (
    'fun',
    'ckeditor',
    'adminsortable',
    'selftest',
    'raven.contrib.django.raven_compat',
    )

ROOT_URLCONF = 'fun.cms.urls'

# Allow all courses to use advanced components
FEATURES['ALLOW_ALL_ADVANCED_COMPONENTS'] = True

# restrain user who can create course in studio to granted ones in CourseCreator table
FEATURES['ENABLE_CREATOR_GROUP'] = True

# LOGGING contant is populated by get_logger_config function called in edx's common settings.
# For sorme reason, not configuring a remote syslogger makes a lot of
# useless messages in logs (TypeError: getsockaddrarg: AF_INET address must be tuple, not NoneType)
# We then remove this logger untill we realy want to configured it
# same in lms.py
#del LOGGING['handlers']['syslogger-remote']
#del LOGGING['loggers']['']['handlers'][LOGGING['loggers']['']['handlers'].index('syslogger-remote')]

# desactivate email sending of stacktrace
del LOGGING['handlers']['mail_admins']
del LOGGING['loggers']['django.request']['handlers'][LOGGING['loggers']['django.request']['handlers'].index('mail_admins')]

# remove newrelic
del LOGGING['handlers']['newrelic']

# Static content
# edX base cms settings file append edx-platform repo. git revision to STATIC_ROOT and STATIC_URL,
# we remove it as we use PipelineCachedStorage for both apps.
STATIC_URL = "/static/"
STATIC_ROOT = "/edx/var/edxapp/staticfiles"


# Enable admin site for university app
#from devstack import FEATURES
FEATURES['ENABLE_DJANGO_ADMIN_SITE'] = True


# add 'theme/cms/templates' directory to MAKO template finder to override some CMS templates...
MAKO_TEMPLATES['main'].insert(0, ENV_ROOT / 'fun-apps/fun/templates/cms')


# #652 we need this to False for course HTML description to be editable
# but it's for now incompatible with working footpage links
# see cms/djangoapps/contentstore/views/course.py:617
FEATURES['ENABLE_MKTG_SITE'] = False
# MKTG_URLS are absolute urls used when ENABLE_MKTG_SITE is set to True
# As FUN theme is not used in CMS, we can not reverse its static pages like /tos or /privacy
MKTG_URL_LINK_MAP = {}
MKTG_URLS = {}
MKTG_URLS['ROOT'] = 'http://' + LMS_BASE
MKTG_URLS['TOS'] = '/tos'
MKTG_URLS['PRIVACY'] = '/privacy'


# from former cms.env.json
FEATURES['AUTH_USE_OPENID_PROVIDER'] = True
FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = False
FEATURES['ADVANCED_SECURITY'] = False
FEATURES['CERTIFICATES_ENABLED'] = True
FEATURES['ENABLE_DISCUSSION_SERVICE'] = True
FEATURES['ENABLE_INSTRUCTOR_ANALYTICS'] = True
FEATURES['ENABLE_S3_GRADE_DOWNLOADS'] = True
FEATURES['SUBDOMAIN_BRANDING'] = False
FEATURES['SUBDOMAIN_COURSE_LISTINGS'] = False
FEATURES['USE_CUSTOM_THEME'] = False

FEATURES['ENFORCE_PASSWORD_POLICY'] = True


CC_PROCESSOR = {
    'CyberSource': {
        'SHARED_SECRET': '',
        'MERCHANT_ID': '',
        'SERIAL_NUMBER': '',
        'ORDERPAGE_VERSION': '7',
        'PURCHASE_ENDPOINT': '',
    }
}

SITE_VARIANT = 'cms'

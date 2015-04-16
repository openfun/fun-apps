# -*- coding: utf-8 -*-

from lms.envs.aws import *  # pylint: disable=wildcard-import, unused-wildcard-import
from ..common import *  # pylint: disable=wildcard-import, unused-wildcard-import

del DEFAULT_FILE_STORAGE  # We do not use S3 file storage backend set in aws.py

# those values also have to be in env.json file,
# because pavlib.utils.envs reads it to build asset's preprocessing commands
THEME_NAME = "fun"
FEATURES['USE_CUSTOM_THEME'] = True
FEATURES['ENABLE_MKTG_SITE'] = False

SITE_NAME = LMS_BASE

# MKTG_URL_LINK_MAP links are named url reverses belonging to Django project
# (also see MKTG_URLS in cms.py)
MKTG_URL_LINK_MAP = {
    "ABOUT": "about",
    "HELP": "help",
    "HONOR": "honor",
    "HOW-IT-WORKS": "how-it-works",
    "TOS": "tos",
    "FAQ": None,
    "PRIVACY": "privacy",
    "CONTACT": None,
    "UNSUPPORTED-BROWSER": "unsupported-browser",
    "LICENSES": "licenses",
    "LEGAL": "legal",
    "COPYRIGHTS": "copyrights",
    "ROOT": 'root',
    'COURSES': 'fun-courses-index',
}
FUN_MKTG_URLS = {}

FEATURES['AUTH_USE_OPENID_PROVIDER'] = True
FEATURES['ADVANCED_SECURITY'] = False
FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = False
FEATURES['CERTIFICATES_ENABLED'] = True
FEATURES['ENABLE_DISCUSSION_SERVICE'] = True
FEATURES['ENABLE_INSTRUCTOR_ANALYTICS'] = False
FEATURES['ALLOW_COURSE_STAFF_GRADE_DOWNLOADS'] = True
FEATURES['ENABLE_S3_GRADE_DOWNLOADS'] = True
FEATURES['PREVIEW_LMS_BASE'] = ''
FEATURES['SUBDOMAIN_BRANDING'] = False
FEATURES['SUBDOMAIN_COURSE_LISTINGS'] = False
FEATURES['ENABLE_DJANGO_ADMIN_SITE'] = True
FEATURES['ACCESS_REQUIRE_STAFF_FOR_COURSE'] = True  # hide spocs from course list
FEATURES['ENABLE_COURSEWARE_INDEX'] = False

#### PASSWORD POLICY SETTINGS #####
FEATURES['ENFORCE_PASSWORD_POLICY'] = True

# Use a FUN-specific root urlconf module
ROOT_URLCONF = 'fun.lms.urls'

INSTALLED_APPS += (
    'fun',
    'adminsortable',
    'courses',
    'course_dashboard',
    'forum_contributors',
    'ckeditor',
    'contact',
    'raven.contrib.django.raven_compat',
    'universities',
    'fun_certificates',
    'fun_instructor',
    'newsfeed',
    'selftest',
    'backoffice',
    )

# replace edX's StaticCountentServer middleware by ours (which generate nice thumbnails)
MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
position = MIDDLEWARE_CLASSES.index('contentserver.middleware.StaticContentServer')
MIDDLEWARE_CLASSES.remove('contentserver.middleware.StaticContentServer')
MIDDLEWARE_CLASSES.insert(position, 'fun.middleware.ThumbnailStaticContentServer')

TEMPLATE_CONTEXT_PROCESSORS += ('fun.context_processor.fun_settings',)

# we customize original edX logging configuration (we should have our own configuration)
# see: edx-platform/common/lib/logsettings.py
# same in cms.py

# LOGGING contant is populated by get_logger_config function called in edx's common settings.
# For sorme reason, not configuring a remote syslogger makes a lot of
# useless messages in logs (TypeError: getsockaddrarg: AF_INET address must be tuple, not NoneType)
# We then remove this logger untill we realy want to configured it
#del LOGGING['handlers']['syslogger-remote']
#del LOGGING['loggers']['']['handlers'][LOGGING['loggers']['']['handlers'].index('syslogger-remote')]

# desactivate email sending of stacktrace
del LOGGING['handlers']['mail_admins']
LOGGING['loggers']['django.request']['handlers'].remove('mail_admins')

# remove newrelic
del LOGGING['handlers']['newrelic']


# add 'forum_contributors' application templates directory to MAKO template finder...
MAKO_TEMPLATES['main'] = [
    ENV_ROOT / 'fun-apps/course_dashboard/templates',
    ENV_ROOT / 'fun-apps/forum_contributors/templates',
] + MAKO_TEMPLATES['main']

# Xiti
XITI_ENABLED = True
XITI_XTN2 = '100'
# static urls are builded using edx-platform git revision
# we have to do so when builing manually xtcore.js static url
from dealer.git import git
XITI_JS_URL = '/static/themes/fun/js/vendor/xtcore.js'
XITI_XTSITE = '530632'
XITI_XTSD = 'https://logs1279'


# Enable help and legal pages
MKTG_URL_LINK_MAP['HELP'] = 'help'
MKTG_URL_LINK_MAP['LEGAL'] = 'legal'

ENABLE_SYSADMIN_DASHBOARD = True

# Allow sending bulk e-mails for all courses
FEATURES['REQUIRE_COURSE_EMAIL_AUTH'] = False

# Registration form fields ('required', 'optional', 'hidden')
REGISTRATION_EXTRA_FIELDS = {
    'level_of_education': 'optional',
    'gender': 'optional',
    'year_of_birth': 'optional',
    'mailing_address': 'optional',
    'goals': 'optional',
    'honor_code': 'required',
    'city': 'required',
    'country': 'required',
}

SITE_VARIANT = 'lms'

# Certificates related settings
CERTIFICATE_BASE_URL = '/attestations/'
CERTIFICATES_DIRECTORY = '/edx/var/edxapp/attestations/'
FUN_LOGO_PATH = BASE_ROOT / 'themes/fun/static/images/logo.png'
STUDENT_NAME_FOR_TEST_CERTIFICATE = 'Test User'

# Grades related settings
GRADES_DOWNLOAD = {
    'STORAGE_TYPE': 'localfs',
    'BUCKET': 'edx-grades',
    'ROOT_PATH': '/edx/var/edxapp/grades',
}

STATIC_ROOT = "/edx/var/edxapp/staticfiles"

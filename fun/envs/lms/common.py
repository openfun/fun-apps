# -*- coding: utf-8 -*-

from lms.envs.aws import *  # pylint: disable=wildcard-import, unused-wildcard-import
from ..common import *  # pylint: disable=wildcard-import, unused-wildcard-import

INSTALLED_APPS += (
    'fun',
    'adminsortable',
    'bootstrapform',
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
    'password_container', # this is an xblock we had to applications to allow syncdb of its models
    'pure_pagination',
    'teachers',
    'faq',
    'edx_gea',
    'djangobower',
    'funsite',
    )

ROOT_URLCONF = 'fun.lms.urls'

update_logging_config(LOGGING)

# Disable S3 file storage
del DEFAULT_FILE_STORAGE

# those values also have to be in env.json file,
# because pavlib.utils.envs reads it to build asset's preprocessing commands
#THEME_NAME = "fun"
#FEATURES['USE_CUSTOM_THEME'] = True
FEATURES['ENABLE_MKTG_SITE'] = False

SITE_NAME = LMS_BASE

# MKTG_URL_LINK_MAP links are named url reverses belonging to Django project
# (also see MKTG_URLS in cms.py)
MKTG_URL_LINK_MAP = {
    "ABOUT": "about",
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

FEATURES['ACCESS_REQUIRE_STAFF_FOR_COURSE'] = True  # hide spocs from course list
FEATURES['ALLOW_COURSE_STAFF_GRADE_DOWNLOADS'] = True
FEATURES['AUTH_USE_OPENID_PROVIDER'] = True
FEATURES['ADVANCED_SECURITY'] = False
FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = False
FEATURES['CERTIFICATES_ENABLED'] = True
FEATURES['ENABLE_COURSEWARE_INDEX'] = False
FEATURES['ENABLE_DISCUSSION_SERVICE'] = True
FEATURES['ENABLE_DJANGO_ADMIN_SITE'] = True
FEATURES['ENABLE_INSTRUCTOR_ANALYTICS'] = False
FEATURES['ENABLE_MAX_FAILED_LOGIN_ATTEMPTS'] = False
FEATURES['ENABLE_S3_GRADE_DOWNLOADS'] = True
FEATURES['PREVIEW_LMS_BASE'] = ''
FEATURES['SUBDOMAIN_BRANDING'] = False
FEATURES['SUBDOMAIN_COURSE_LISTINGS'] = False
FEATURES['ENFORCE_PASSWORD_POLICY'] = True
FEATURES['ENABLE_CONTENT_LIBRARIES'] = False  # Content libraries support requires new coursekey format

# replace edX's StaticContentServer middleware by ours (which generates nice thumbnails)
MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
MIDDLEWARE_CLASSES[
    MIDDLEWARE_CLASSES.index('contentserver.middleware.StaticContentServer')
] = 'fun.middleware.ThumbnailStaticContentServer'

TEMPLATE_CONTEXT_PROCESSORS += ('fun.context_processor.fun_settings',)

# add application templates directory to MAKO template finder
MAKO_TEMPLATES['main'] = [
    FUN_BASE_ROOT / 'funsite/templates/lms',   # overrides template in edx-platform/lms/templates
    FUN_BASE_ROOT / 'funsite/templates',
    FUN_BASE_ROOT / 'courses/templates',
    FUN_BASE_ROOT / 'course_dashboard/templates',
    FUN_BASE_ROOT / 'forum_contributors/templates',
] + MAKO_TEMPLATES['main']

# Xiti
XITI_ENABLED = True
XITI_XTN2 = '100'
XITI_JS_URL = '/static/themes/fun/js/vendor/xtcore.js'
XITI_XTSITE = '530632'
XITI_XTSD = 'https://logs1279'


# Enable legal page
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
GRADES_DOWNLOAD_ROUTING_KEY = None

PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 10,
    'MARGIN_PAGES_DISPLAYED': 10,
}

ACCOUNT_VISIBILITY_CONFIGURATION["default_visibility"] = "private"

# We user Bower to handle our own CSS/Javascript dependencies
STATICFILES_FINDERS += ('fun.utils.staticfiles_finders.BowerFinder',)
BOWER_COMPONENTS_ROOT = FUN_BASE_ROOT + '/components/'
BOWER_PATH = '/usr/bin/bower'
# JS libraries will be downloaded to fun-apps/components/bower_components by `fun lms.dev bower install` command,
# then collectected with other statics
BOWER_INSTALLED_APPS = (
    'bootstrap-big-grid',  # http://benwhitehead.github.io/
    'jquery',
    'arg.js',
    'OwlCarousel2',
)

# -*- coding: utf-8 -*-

from lms.envs.aws import *  # pylint: disable=wildcard-import, unused-wildcard-import
from ..common import *  # pylint: disable=wildcard-import, unused-wildcard-import

INSTALLED_APPS += (
    'rest_framework.authtoken',

    'backoffice',
    'fun',
    'funsite',
    'fun_api',
    'fun_certificates',
    'fun_instructor',
    'contact',
    'course_dashboard',
    'courses',
    'courses_api',
    'course_pages',
    'newsfeed',
    'universities',
    'videoproviders',

    'easy_thumbnails',
    'bootstrapform',
    'ckeditor',
    'raven.contrib.django.raven_compat',
    'pure_pagination',

    'forum_contributors',
    'selftest',
    'password_container', # this is an xblock we add to applications to allow syncdb of its models
    'teachers',
    'faq',
    'edx_gea',
    )

ROOT_URLCONF = 'fun.lms.urls'

update_logging_config(LOGGING)

# Disable S3 file storage
del DEFAULT_FILE_STORAGE

# those values also have to be in env.json file,
# because pavlib.utils.envs reads it to build asset's preprocessing commands
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
    "COPYRIGHTS": None,
    "ROOT": 'root',
    'COURSES': 'fun-courses:index',
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
    FUN_BASE_ROOT / 'course_pages/templates',
    FUN_BASE_ROOT / 'course_dashboard/templates',
    FUN_BASE_ROOT / 'forum_contributors/templates',
    FUN_BASE_ROOT / 'newsfeed/templates',
] + MAKO_TEMPLATES['main']

# Add funsite templates directory to Django templates finder.
TEMPLATE_DIRS.insert(0, FUN_BASE_ROOT / 'funsite/templates/lms')

# Xiti
XITI_ENABLED = True
XITI_XTN2 = '100'
XITI_JS_URL = '/static/funsite/xiti/xtcore.js'
XITI_XTSITE = '530632'
XITI_XTSD = 'https://logs1279'


# Enable legal page
MKTG_URL_LINK_MAP['LEGAL'] = 'legal'

# Allow sending bulk e-mails for all courses
FEATURES['REQUIRE_COURSE_EMAIL_AUTH'] = False

# Access to sysadmin view (users, courses information. User has to be staff, see navigation.html)
FEATURES['ENABLE_SYSADMIN_DASHBOARD'] = False

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

FUN_SMALL_LOGO_RELATIVE_PATH = 'funsite/images/logos/fun61.png'
FUN_BIG_LOGO_RELATIVE_PATH = 'funsite/images/logos/fun195.png'

# Certificates related settings
CERTIFICATE_BASE_URL = '/attestations/'
CERTIFICATES_DIRECTORY = '/edx/var/edxapp/attestations/'
FUN_LOGO_PATH = FUN_BASE_ROOT / 'funsite/static' / FUN_BIG_LOGO_RELATIVE_PATH
STUDENT_NAME_FOR_TEST_CERTIFICATE = 'Test User'

# Grades related settings
GRADES_DOWNLOAD = {
    'STORAGE_TYPE': 'localfs',
    'BUCKET': 'edx-grades',
    'ROOT_PATH': '/edx/var/edxapp/grades',
}
GRADES_DOWNLOAD_ROUTING_KEY = None


# Our new home page is so shiny and chrome that users must see it more often
FEATURES['ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER'] = False

# ??
PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 10,
    'MARGIN_PAGES_DISPLAYED': 10,
}

NUMBER_DAYS_TOO_LATE = 7

# Default visibility of student's profile to other students
ACCOUNT_VISIBILITY_CONFIGURATION["default_visibility"] = "private"

# easy-thumbnails
SOUTH_MIGRATION_MODULES['easy_thumbnails'] = 'easy_thumbnails.south_migrations'

# Add our v3 CSS and JS files to assets compilation pipeline to make them available in courseware.
# On FUN v3 frontend, which do not use edX's templates, those files are loaded
# by funsite/templates/funsite/parts/base.html and css/lms-main.css

PIPELINE_CSS['style-main']['source_filenames'].append('fun/css/cookie-banner.css')
PIPELINE_CSS['style-main']['source_filenames'].append('funsite/css/header.css')
PIPELINE_CSS['style-main']['source_filenames'].append('funsite/css/footer.css')
PIPELINE_CSS['style-main']['source_filenames'].append('forum_contributors/highlight/css/highlight.css')

# js/lms-application.js
PIPELINE_JS['application']['source_filenames'].append('fun/js/cookie-banner.js')
PIPELINE_JS['application']['source_filenames'].append('funsite/js/header.js')

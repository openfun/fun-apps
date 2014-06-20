# -*- coding: utf-8 -*-

from .devstack import *  # pylint: disable=wildcard-import, unused-wildcard-import

# Add the fun-apps repo to sys.path:
import sys
sys.path.append('/edx/app/edxapp/fun-apps')

FEATURES['USE_CUSTOM_THEME'] = True

# Use a FUN-specific root urlconf module
ROOT_URLCONF = 'fun.lms.urls'

INSTALLED_APPS += (
    'django_extensions',
    'universities',
    'ckeditor',
    'adminsortable',
    'contact',
    )


MEDIA_URL = '/media/'
MEDIA_ROOT = "/edx/var/edxapp/uploads"
STATIC_ROOT = '/edx/var/edxapp/staticfiles'

CKEDITOR_UPLOAD_PATH = '../uploads/'   # ?

# Xiti
XITI_ENABLED = True
XITI_XTN2 = "101"
# Note: XITI_JS_URL has been changed! Old value commented...
# XITI_JS_URL = "/static/themes/fun/js/vendor/xtcore.5c15ffd8e0b9.js"
XITI_JS_URL = "/static/themes/fun/js/vendor/xtcore.js"
XITI_XTSITE = "530632"
XITI_XTSD = "https://logs1279"

# Locale path
LOCALE_PATHS = (
  '/edx/app/edxapp/fun-apps/locale',
  '/edx/app/edxapp/edx-platform/conf/locale',
)

# Enable admin site for university app
#from devstack import FEATURES
FEATURES['ENABLE_DJANGO_ADMIN_SITE'] = True

# Enable help and legal pages
from aws import MKTG_URL_LINK_MAP
MKTG_URL_LINK_MAP['HELP'] = 'help'
MKTG_URL_LINK_MAP['LEGAL'] = 'legal'

# Address to which contact emails should be sent
CONTACT_EMAIL = 'contact@france-universite-numerique-mooc.fr'

# Blacklist a few middlewares that do not work properly
from devstack import MIDDLEWARE_CLASSES
BLACKLISTED_MIDDLEWARE_CLASSES = (
  'lang_pref.middleware.LanguagePreferenceMiddleware',
  'dark_lang.middleware.DarkLangMiddleware',
)
MIDDLEWARE_CLASSES = tuple(m for m in MIDDLEWARE_CLASSES if not m in BLACKLISTED_MIDDLEWARE_CLASSES)

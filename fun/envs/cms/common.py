# -*- coding: utf-8 -*-

from cms.envs.aws import *  # pylint: disable=wildcard-import, unused-wildcard-import
from ..common import *  # pylint: disable=wildcard-import, unused-wildcard-import


INSTALLED_APPS += (
    'fun',
    'ckeditor',
    'adminsortable',
    'selftest',
    'raven.contrib.django.raven_compat',
    )

ROOT_URLCONF = 'fun.cms.urls'

# edX base cms settings file appends the git revision of the edx-platform repo
# git revision to STATIC_ROOT and STATIC_URL.  We remove it as we use
# PipelineCachedStorage for both apps.
STATIC_URL = "/static/"

update_logging_config(LOGGING)

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

# Allow all courses to use advanced components
FEATURES['ALLOW_ALL_ADVANCED_COMPONENTS'] = True
FEATURES['AUTH_USE_OPENID_PROVIDER'] = True
FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = False
FEATURES['ADVANCED_SECURITY'] = False
FEATURES['CERTIFICATES_ENABLED'] = True
FEATURES['ENABLE_CONTENT_LIBRARIES'] = False  # Content libraries support requires new coursekey format
# restrain user who can create course in studio to granted ones in CourseCreator table
FEATURES['ENABLE_CREATOR_GROUP'] = True
FEATURES['ENABLE_DISCUSSION_SERVICE'] = True
FEATURES['ENABLE_DJANGO_ADMIN_SITE'] = True
FEATURES['ENABLE_INSTRUCTOR_ANALYTICS'] = True
FEATURES['ENABLE_MAX_FAILED_LOGIN_ATTEMPTS'] = False
FEATURES['ENABLE_S3_GRADE_DOWNLOADS'] = True
FEATURES['ENFORCE_PASSWORD_POLICY'] = True
FEATURES['IS_EDX_DOMAIN'] = True  # used to display Edx Studio logo, see edx-platform/cms/templates/widgets/header.html
FEATURES['SUBDOMAIN_BRANDING'] = False
FEATURES['SUBDOMAIN_COURSE_LISTINGS'] = False
FEATURES['USE_CUSTOM_THEME'] = False

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

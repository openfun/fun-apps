# -*- coding: utf-8 -*-
"""
Specific LMS settings for developpement environement
"""

from .common import *
from ..dev import *

SITE_NAME = LMS_BASE

SERVER_EMAIL = '%s-%s@france-universite-numerique-mooc.fr' % (ENVIRONMENT, SITE_VARIANT)



PIPELINE_SASS_ARGUMENTS = PIPELINE_SASS_ARGUMENTS.format(proj_dir=PROJECT_ROOT)

INSTALLED_APPS += ('django_extensions',)

################################ DEBUG TOOLBAR ################################

INSTALLED_APPS += DEBUG_TOOLBAR_INSTALLED_APPS
MIDDLEWARE_CLASSES += DEBUG_TOOLBAR_MIDDLEWARE_CLASSES

########################### VERIFIED CERTIFICATES #################################

FEATURES['AUTOMATIC_VERIFY_STUDENT_IDENTITY_FOR_TESTING'] = True
FEATURES['ENABLE_PAYMENT_FAKE'] = True
FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = True

MAKO_MODULE_DIR = None   # this will prevent Mako to cache generated files
# To totaly deactivate cache we also have de deactivate edx cache on anonymous views
# by commenting line 79 (cache.set(cache_key, response, 60 * 3)) in file common/djangoapps/util/cache.py@cache_if_anonymous

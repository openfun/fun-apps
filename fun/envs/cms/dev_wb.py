# -*- coding: utf-8 -*-
"""
Specific CMS settings for developpement environement
"""

import sys
from path import path
BASE_ROOT = path('/edx/app/edxapp/')
FUN_BASE_ROOT = BASE_ROOT / "fun-apps"
sys.path.append(FUN_BASE_ROOT)


from fun.envs.cms.common_wb import *
from fun.envs.dev_wb import *

BULK_SMTP_SERVER = 'localhost'
TRANSACTIONAL_SMTP_SERVER = 'localhost'
EMAIL_BACKEND = 'fun.smtp.backend.MultipleSMTPEmailBackend'
EMAIL_HOST = {
    'bulk': {'host': BULK_SMTP_SERVER, 'port': 25, 'username': 'username', 'password': 'password'},
    'transactional': {'host': TRANSACTIONAL_SMTP_SERVER, 'port': 25, 'username': None, 'password': None}
    }


PLATFORM_NAME = u"Marque blanche"
ENVIRONMENT = 'mb'
LMS_BASE = 'localhost:8000'
CMS_BASE = 'localhost:8001'
SITE_NAME = LMS_BASE

LMS_ROOT_URL = "http://{}".format(LMS_BASE)
SITE_VARIANT = 'lms'
SERVER_EMAIL = '%s-%s@%s' % (ENVIRONMENT, SITE_VARIANT, SITE_NAME)



SERVER_EMAIL = '%s-%s@france-universite-numerique-mooc.fr' % (ENVIRONMENT, SITE_VARIANT)

PIPELINE_SASS_ARGUMENTS = PIPELINE_SASS_ARGUMENTS.format(proj_dir=PROJECT_ROOT)

INSTALLED_APPS += ('django_extensions',)

################################ DEBUG TOOLBAR ################################

#INSTALLED_APPS += DEBUG_TOOLBAR_INSTALLED_APPS
#MIDDLEWARE_CLASSES += DEBUG_TOOLBAR_MIDDLEWARE_CLASSES

########################### VERIFIED CERTIFICATES #################################

FEATURES['AUTOMATIC_VERIFY_STUDENT_IDENTITY_FOR_TESTING'] = True
FEATURES['ENABLE_PAYMENT_FAKE'] = True
FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = True

FEATURES['ENABLE_COMBINED_LOGIN_REGISTRATION'] = False

## MAKO_MODULE_DIR = None   # this will prevent Mako to cache generated files

# To totaly deactivate cache we also have de deactivate edx cache on anonymous views
# by commenting line 79 (cache.set(cache_key, response, 60 * 3)) in file common/djangoapps/util/cache.py@cache_if_anonymous

HAYSTACK_CONNECTIONS = configure_haystack(ELASTIC_SEARCH_CONFIG)


# development ecommerce settings

# If your development environment is not exposed to internet and can not receive payment processor notification
# by settings this to True, the success return page will generate the appropriate POST to ecommerce service
FUN_ECOMMERCE_DEBUG_NO_NOTIFICATION = True
FEATURES['ENABLE_AUTO_AUTH'] = True
ECOMMERCE_API_URL = "http://ecomdev.local/api/v2/"
ECOMMERCE_PUBLIC_URL_ROOT = "http://ecomdev.local"
ECOMMERCE_NOTIFICATION_URL = 'http://ecomdev.local/payment/paybox/notify/'
JWT_ISSUER = "http://funbox.local:8000/oauth2"

PIPELINE_ENABLED = False  # We can not activate PIPELINE in dev env. therefore we will not use aggregated static files

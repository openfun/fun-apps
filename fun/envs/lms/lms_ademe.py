# -*- coding: utf-8 -*-


# FUN_BASE_ROOT should be added to Python PATH before importing this file
import sys
from path import path
BASE_ROOT = path('/edx/app/edxapp/')
FUN_BASE_ROOT = BASE_ROOT / "fun-apps"
sys.path.append(FUN_BASE_ROOT)



from .common_wb import *


PLATFORM_NAME = u"Mooc Bâtiment durable"
ENVIRONMENT = 'ademe'
LMS_BASE = 'mooc-batiment-durable.fr'
CMS_BASE = 'mooc-batiment-durable.fr:18010'
SITE_NAME = LMS_BASE

LMS_ROOT_URL = "http://{}".format(LMS_BASE)
SITE_VARIANT = 'lms'
GOOGLE_ANALYTICS_ACCOUNT = 'UA-87930856-1'
SERVER_EMAIL = '%s-%s@%s' % (ENVIRONMENT, SITE_VARIANT, SITE_NAME)




DEFAULT_FROM_EMAIL = "contact@" + SITE_NAME
DEFAULT_FEEDBACK_EMAIL = "contact@" + SITE_NAME
DEFAULT_BULK_FROM_EMAIL = "contact@" + SITE_NAME
TECH_SUPPORT_EMAIL = "contact@" + SITE_NAME
CONTACT_EMAIL = "contact@" + SITE_NAME
BUGS_EMAIL = "contact@" + SITE_NAME
PAYMENT_SUPPORT_EMAIL = "contact@" + SITE_NAME
PAYMENT_ADMIN = "contact@" + SITE_NAME
# STATS emails are used by fun/management/commands/enrollment_statistics.py
STATS_EMAIL = "contact@" + SITE_NAME

BULK_EMAIL_DEFAULT_FROM_EMAIL = "no-reply" + SITE_NAME
FAVICON_PATH = ''


PLATFORM_FACEBOOK_ACCOUNT = 'https://www.facebook.com/france.universite.numerique'
PLATFORM_TWITTER_ACCOUNT = '@funmooc'

ADMINS = [['funteam', 'richard@openfun.fr']]




RAVEN_CONFIG = {
    'dsn': '',
}

update_logging_config(LOGGING)

def configure_raven(sentry_dsn, raven_config, logging_config):
    logging_config['handlers']['sentry']['dsn'] = sentry_dsn
    raven_config['dsn'] = sentry_dsn

configure_raven('http://7c7666e0e4b043aa96e4d7f1851faf3a:3fe6fb7ca3a849a196a480fceeef3b82@infrasentry.cines.openfun.fr/2',
                RAVEN_CONFIG, LOGGING)

EMAIL_BACKEND = 'fun.smtp.backend.MultipleSMTPEmailBackend'
EMAIL_HOST = {
    # Bulk uses Amazon SES, User: `ses-smtp-user.20161209-105613-ademe`
    'bulk': {'host': 'email-smtp.eu-west-1.amazonaws.com', 'port': 587,
             'username': 'AKIAJSJYRZWLZYGDVSOQ', 'password': 'Aq0hZa0Ari7l38q9VPZKeFheJi7b9ZwIqxdN3vPuTEpV',
             'use_tls': True},
    # Transactionnel uses localhost as relay to Mandrill with sub-account `ademe`
    'transactional': {'host': 'localhost', 'port': 25}
    }


HAYSTACK_CONNECTIONS = configure_haystack(ELASTIC_SEARCH_CONFIG)




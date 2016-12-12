# -*- coding: utf-8 -*-

import imp
from glob import glob
import os
import sys

from path import path

BASE_ROOT = path('/edx/app/edxapp/')  # folder where edx-platform main repository and our stuffs are
FUN_BASE_ROOT = BASE_ROOT / "fun-apps"
sys.path.append(FUN_BASE_ROOT)



# those 2 constants are used in code to describe certificate, they are not i18ned, you could do it
CERT_NAME_SHORT = u"Attestation"
CERT_NAME_LONG = u"Attestation de réussite"



TIME_ZONE = 'Europe/Paris'

# i18n
USE_I18N = True
gettext = lambda s: s

# This is the folder where all file data will be shared between the instances
# of the same environment.

CKEDITOR_UPLOAD_PATH = './'


LOCAL_LOGLEVEL = 'INFO'
LOGGING_ENV = 'sandbox'
LOG_DIR = '/edx/var/logs/edx'

# Max size of asset uploads to GridFS
MAX_ASSET_UPLOAD_FILE_SIZE_IN_MB = 30

SEGMENT_IO_LMS = True
PAID_COURSE_REGISTRATION_CURRENCY = ["usd", "$"]
SEGMENT_IO_LMS = True

# Locale path
LOCALIZED_APPS = sorted([p.split("/")[-2] for p in glob(FUN_BASE_ROOT / "*/locale")])
LOCALE_PATHS = tuple(
    [FUN_BASE_ROOT / app / "locale" for app in LOCALIZED_APPS] +
    [
        BASE_ROOT / 'edx-platform/conf/locale',
        BASE_ROOT / 'venvs/edxapp/lib/python2.7/site-packages/django_countries/locale',    # this should not be required
        BASE_ROOT / 'venvs/edxapp/src/edx-proctoring/locale',
    ]
)

# Custom password policy will be activated by FEATURES['ENFORCE_PASSWORD_POLICY'] = True
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 30
PASSWORD_COMPLEXITY = {
      'UPPER': 1,
      'LOWER': 1,
      'DIGITS': 1
}

# This force Edx Studio to use our own video provider Xblock on default button
FUN_DEFAULT_VIDEO_PLAYER = 'libcast_xblock'

def prefer_fun_xmodules(identifier, entry_points):
    """
    Make sure that we use the correct FUN xmodule for video in the studio
    """
    from django.conf import settings
    from xmodule.modulestore import prefer_xmodules
    if identifier == 'video' and settings.FUN_DEFAULT_VIDEO_PLAYER is not None:
        import pkg_resources
        from xblock.core import XBlock
        # These entry points are listed in the setup.py of the libcast module
        # Inspired by the XBlock.load_class method
        entry_points = list(pkg_resources.iter_entry_points(XBlock.entry_point,
                name=settings.FUN_DEFAULT_VIDEO_PLAYER))
    return prefer_xmodules(identifier, entry_points)

XBLOCK_SELECT_FUNCTION = prefer_fun_xmodules
#######




# easy-thumbnails
THUMBNAIL_PRESERVE_EXTENSIONS = True
THUMBNAIL_EXTENSION = 'png'

# Course image thumbnail sizes
FUN_THUMBNAIL_OPTIONS = {
    'small': {'size': (270, 152), 'crop': 'smart'},
    'big': {'size': (337, 191), 'crop': 'smart'},
    'about': {'size': (730, 412), 'crop': 'scale'},
    'facebook': {'size': (600, 315), 'crop': 'smart'},  # https://developers.facebook.com/docs/sharing/best-practices
}


SHARED_ROOT = '/edx/var/edxapp/shared'
MEDIA_ROOT = '/edx/var/edxapp/uploads'
MEDIA_URL = '/media/'

# ora2 fileupload
ORA2_FILEUPLOAD_BACKEND = "filesystem"
ORA2_FILEUPLOAD_ROOT = os.path.join(SHARED_ROOT, "openassessment_submissions")
ORA2_FILEUPLOAD_CACHE_ROOT = os.path.join(SHARED_ROOT, "openassessment_submissions_cache")
ORA2_FILEUPLOAD_CACHE_NAME = "openassessment_submissions"
FILE_UPLOAD_STORAGE_BUCKET_NAME = "uploads"

# Profile image upload
PROFILE_IMAGE_BACKEND = {
    'class': 'storages.backends.overwrite.OverwriteStorage',
    'options': {
        'location': os.path.join(MEDIA_ROOT, 'profile-images/'),
        'base_url': os.path.join(MEDIA_URL, 'profile-images/'),
    },
}

ANONYMIZATION_KEY = """dummykey"""


def update_logging_config(logging_config):
    """
    Call this function with the LOGGING variable to configure some additional
    loggers.
    """
    # Deactivate email sending of stacktrace
    logging_config['handlers'].pop('mail_admins', None)
    if 'mail_admins' in logging_config['loggers']['django.request']['handlers']:
        logging_config['loggers']['django.request']['handlers'].remove('mail_admins')

    # Remove newrelic
    logging_config['handlers'].pop('newrelic', None)

    # Send all errors to sentry
    logging_config['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.handlers.logging.SentryHandler',
        'dsn': '',  # don't forget to update this once you know the sentry dsn
    }
    if 'sentry' not in logging_config['loggers']['']['handlers']:
        logging_config['loggers']['']['handlers'].append('sentry')

# FUN Mongo database
# Other settings FUN_MONGO_HOST, FUN_MONGO_USER and FUN_MONGO_PASSWORD will come from lms/cms.auth.env
FUN_MONGO_DATABASE = 'fun'

SEARCH_ENGINE = 'search.elastic.ElasticSearchEngine'  # use ES for courseware and course meta information indexing
ELASTIC_SEARCH_CONFIG = [{'host': 'localhost'},]  # specific environments will override this setting

ELASTICSEARCH_INDEX_SETTINGS = {
    "settings": {
        "analysis": {
            "filter": {
                "elision": {
                    "type": "elision",
                    "articles": ["l", "m", "t", "qu", "n", "s", "j", "d"]
                }
            },
            "analyzer": {
                "custom_french_analyzer": {
                    "tokenizer": "letter",
                    "filter": ["asciifolding", "lowercase", "french_stem", "elision", "stop", "word_delimiter"]
                },
            },
        }
    }
}
def configure_haystack(elasticsearch_conf):
    """Configure haystack with env. specific ES conf."""
    return {
        'default': {
            'ENGINE': 'courses.search_indexes.ConfigurableElasticSearchEngine',
            'URL': 'http://%s:%d/' % (elasticsearch_conf[0].get('host', 'localhost'), elasticsearch_conf[0].get('port', 9200)),
            'INDEX_NAME': 'haystack',
        },
    }


# Global CKeditor configuration, used for University and Article ModelAdmin
CKEDITOR_CONFIGS = {
    'default': {
       'toolbar': [
            [      'Undo', 'Redo',
              '-', 'Bold', 'Italic', 'Underline',
              '-', 'Link', 'Unlink', 'Anchor',
              '-', 'Format',
              '-', 'SpellChecker', 'Scayt',
              '-', 'Maximize',
            ],
            [      'HorizontalRule',
              '-', 'Table',
              '-', 'BulletedList', 'NumberedList',
              '-', 'Cut','Copy','Paste','PasteText','PasteFromWord',
              '-', 'SpecialChar',
              '-', 'Source',
            ]
        ],
        'toolbarCanCollapse': False,
        'entities': False,
        'width': 955,
        'uiColor': '#9AB8F3',
    }
}

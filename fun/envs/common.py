# -*- coding: utf-8 -*-

import imp
from glob import glob
import os
import sys

from path import path

BASE_ROOT = path('/edx/app/edxapp/')  # folder where edx-platform main repository and our stuffs are
FUN_BASE_ROOT = BASE_ROOT / "fun-apps"
sys.path.append(FUN_BASE_ROOT)

PLATFORM_NAME = "FUN"
DEFAULT_FROM_EMAIL = "inscription@france-universite-numerique-mooc.fr"
DEFAULT_FEEDBACK_EMAIL = "contact@france-universite-numerique-mooc.fr"
DEFAULT_BULK_FROM_EMAIL = "cours@france-universite-numerique-mooc.fr"
TECH_SUPPORT_EMAIL = "helpdesk@france-universite-numerique-mooc.fr"
CONTACT_EMAIL = "contact@france-universite-numerique-mooc.fr"
BUGS_EMAIL = "bugs@france-universite-numerique-mooc.fr"
PAYMENT_SUPPORT_EMAIL = "paiements@fun-mooc.fr"
PAYMENT_ADMIN = "paybox@fun-mooc.fr"
# STATS emails are used by fun/management/commands/enrollment_statistics.py
STATS_EMAIL = "info@france-universite-numerique-mooc.fr"
STATS_RECIPIENTS = ['moocadmin@cines.fr', 'info@france-universite-numerique-mooc.fr', 'funmooc@groupes.renater.fr']
BULK_EMAIL_DEFAULT_FROM_EMAIL = "no-reply@france-universite-numerique-mooc.fr"
FAVICON_PATH = "fun/images/favicon.ico"

PLATFORM_FACEBOOK_ACCOUNT = 'https://www.facebook.com/france.universite.numerique'
PLATFORM_TWITTER_ACCOUNT = '@funmooc'

# those 2 constants are used in code to describe certificate, they are not i18ned, you could do it
CERT_NAME_SHORT = u"Attestation"
CERT_NAME_LONG = u"Attestation de réussite"

ADMINS = [['funteam', 'dev@france-universite-numerique-mooc.fr']]

SESSION_COOKIE_DOMAIN = None

# we use mysql to store mutualize session persistance between Django instances
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

WIKI_ENABLED = True

LMS_SEGMENT_KEY = None   # Dogwood: Probably related to google analytics.

TIME_ZONE = 'Europe/Paris'

# i18n
USE_I18N = True
gettext = lambda s: s

LANGUAGE_CODE = 'fr'
# These are the languages we allow on FUN platform
# DarkLanguageConfig.released_languages must use the same codes (comma separated)
LANGUAGES = (
    ('fr', 'Français'),
    ('en', 'English'),
    ('de-de', 'Deutsch'),  # codes have to match edX's ones (lms.envs.common.LANGUAGES)
)
# EdX rely on this code to display current language to user, when not yet set in preferences
# This is probably a bug because user with an english browser, will have the english i18n
# still, when not set, the preference page will show 'fr' as default language.
# (student.views.dashboard use settings.LANGUAGE instead of request.LANGUAGE)

PIPELINE = True  # use djangopipeline aggregated css and js file (in production)
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = "/edx/var/edxapp/uploads"

STATIC_ROOT = "/edx/var/edxapp/staticfiles"

# This is the folder where all file data will be shared between the instances
# of the same environment.
SHARED_ROOT = '/edx/var/edxapp/shared'

CKEDITOR_UPLOAD_PATH = './'
CKEDITOR_CONFIGS = {
    'default': {
    },
    'news': {
        # Redefine path where the news images/files are uploaded. This would
        # better be done at runtime with the 'reverse' function, but
        # unfortunately there is no way around defining this in the settings
        # file.
        'filebrowserUploadUrl': '/news/ckeditor/upload/',
        'filebrowserBrowseUrl': '/news/ckeditor/browse/',
        'toolbar_Full': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Image', 'Flash', 'Table', 'HorizontalRule'],
            ['NumberedList', 'BulletedList', 'Blockquote', 'TextColor', 'BGColor'],
            ['Smiley', 'SpecialChar'], ['Source'],
        ],
    },
}

SYSLOG_SERVER = ''

SITE_NAME = 'localhost'   # probably not good for production

FEEDBACK_SUBMISSION_EMAIL = ''


GRADES_DOWNLOAD = {
        "BUCKET": "edx-grades",
        "ROOT_PATH": "/tmp/edx-s3/grades",
        "STORAGE_TYPE": "localfs"
    }

HOSTNAME_MODULESTORE_DEFAULT_MAPPINGS = {
        "preview\\.": "draft"
    }

GITHUB_REPO_ROOT = '/edx/var/edxapp/data'

# This settings may have to be changed when final URL scheme will be decided for production
LMS_BASE = 'fun-mooc.fr'  # LMS web address
CMS_BASE = 'studio.fun-mooc.fr'  # Studio web address
# We do not need to prefix LMS_BASE to access LMS from studio in our configuration,
# but we may want to use a 'preview' instance of LMS as in v1
PREVIEW_LMS_BASE = ''  # Sudio will build preview address like this //PREVIEW_LMS_BASE + LMS_BASE to/course...

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


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'infrasmtp02.cines.openfun.fr'   # we will use the new smtp for transactional emails on all instances

BULK_SMTP_SERVER = 'smtpmooc.cines.openfun.fr'  # old server will only be used for bulk email on brick lms
TRANSACTIONAL_SMTP_SERVER = EMAIL_HOST

ANALYTICS_SERVER_URL = ''
BOOK_URL = ''

COMMENTS_SERVICE_KEY = 'password'
COMMENTS_SERVICE_URL = 'http://localhost:18080'

CAS_ATTRIBUTE_CALLBACK = ''
CAS_EXTRA_LOGIN_PARAMS = ''
CAS_SERVER_URL = ''

BROKER_URL = 'amqp://guest@127.0.0.1:5672'  # may work on devstack, production envs. have own conf.

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'

CERT_QUEUE = 'certificates'
CMS_BASE = ''
CODE_JAIL = {
    "limits": {
        "REALTIME": 5,
        "VMEM": 50 * 1000 * 1000,
    },
    "python_bin": "",
    "user": "sandbox"
}

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

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
ensure_directory_exists(ORA2_FILEUPLOAD_ROOT)
ensure_directory_exists(ORA2_FILEUPLOAD_CACHE_ROOT)

# Caches
def default_cache_configuration(key_prefix):
    return {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "util.memcache.safe_key",
        "KEY_PREFIX": key_prefix,
        "LOCATION": [
            "localhost:11211"
        ]
    }

def file_cache_configuration(key_prefix, subfolder_name):
    cache_path = os.path.join(SHARED_ROOT, subfolder_name)
    ensure_directory_exists(cache_path)
    return {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        "KEY_FUNCTION": "util.memcache.safe_key",
        "KEY_PREFIX": key_prefix,
        "LOCATION": cache_path
    }

CACHES = {
    "celery": default_cache_configuration("integration_celery"),
    "default": default_cache_configuration("sandbox_default"),
    "general": default_cache_configuration("sandbox_general"),
    "libcast_resources": file_cache_configuration("resources", "libcast_cache"),
    "video_subtitles": file_cache_configuration(
        "video_subtitles",
        "video_subtitles_cache"
    ),
    "mongo_metadata_inheritance": default_cache_configuration("integration_mongo_metadata_inheritance"),
    "staticfiles": default_cache_configuration("integration_static_files"),

    ORA2_FILEUPLOAD_CACHE_NAME: file_cache_configuration(
        "openassessment_submissions",
        "openassessment_submissions_cache"
    )
}

ANONYMIZATION_KEY = """dummykey"""

RAVEN_CONFIG = {
    'dsn': '',
}

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

def configure_raven(sentry_dsn, raven_config, logging_config):
    logging_config['handlers']['sentry']['dsn'] = sentry_dsn
    raven_config['dsn'] = sentry_dsn

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

PROCTORU_API = 'x.proctoru.com'  # preprod api
PROCTORU_TOKEN = 'f0ef8b49-51e6-4009-8db3-6b87d77f40d1'  # preprod auth token

def get_proctoru_app_if_available():
    try:
        imp.find_module('proctoru')
        return ('proctoru',)
    except ImportError:
        return ()

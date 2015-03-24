# -*- coding: utf-8 -*-

from glob import glob
import sys
import gettext

from path import path
from dealer.git import git

BASE_ROOT = path('/edx/app/edxapp/')  # folder where edx-platform main repository and our stuffs are

sys.path.append('/edx/app/edxapp/fun-apps') # Add the fun-apps repo to sys.path:

PLATFORM_NAME = "FUN"
DEFAULT_FROM_EMAIL = "inscription@france-universite-numerique-mooc.fr"
DEFAULT_FEEDBACK_EMAIL = "feedback@france-universite-numerique-mooc.fr"
DEFAULT_BULK_FROM_EMAIL = "cours@france-universite-numerique-mooc.fr"
TECH_SUPPORT_EMAIL = "helpdesk@france-universite-numerique-mooc.fr"
CONTACT_EMAIL = "contact@france-universite-numerique-mooc.fr"
BUGS_EMAIL = "bugs@france-universite-numerique-mooc.fr"
PAYMENT_SUPPORT_EMAIL = "paiements@france-universite-numerique-mooc.fr"
# STATS emails are used by fun-apps/fun/management/commands/enrollment_statistics.py
STATS_EMAIL = "info@france-universite-numerique-mooc.fr"
STATS_RECIPIENTS = ['moocadmin@cines.fr', 'info@france-universite-numerique-mooc.fr', 'funmooc@groupes.renater.fr']
BULK_EMAIL_DEFAULT_FROM_EMAIL = "no-reply@france-universite-numerique-mooc.fr"

ADMINS = [['funteam', 'dev@france-universite-numerique-mooc.fr']]

SESSION_COOKIE_DOMAIN = None

# we use mysql to store mutualize session persistance between Django instances
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

WIKI_ENABLED = True

TIME_ZONE = 'Europe/Paris'

# i18n
USE_I18N = True
gettext = lambda s: s

LANGUAGE_CODE = 'fr'
# These are the languages we allow on FUN platform
# DarkLanguageConfig.released_languages must use the same codes (comma separated)
LANGUAGES = (
    ('fr', gettext('French')),
    ('en', gettext('English')),
    ('de-de', gettext('German')), # codes have to match edX's ones (lms.envs.common.LANGUAGES)
)
# EdX rely on this code to display current language to user, when not yet set in preferences
# This is probably a bug because user with an english browser, will have the english i18n
# still, when not set, the preference page will show 'fr' as default language.
# (student.views.dashboard use settings.LANGUAGE instead of request.LANGUAGE)

PIPELINE = True  # use djangopipeline aggregated css and js file (in production)
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = "/edx/var/edxapp/uploads"

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
LMS_BASE = 'france-universite-numerique-mooc.fr'  # LMS web address
CMS_BASE = 'studio.france-universite-numerique-mooc.fr'  # Studio web address
# We do not need to prefix LMS_BASE to access LMS from studio in our configuration,
# but we may want to use a 'preview' instance of LMS as in v1
PREVIEW_LMS_BASE = ''  # Sudio will build preview address like this //PREVIEW_LMS_BASE + LMS_BASE to/course...


LOCAL_LOGLEVEL = 'INFO'
LOGGING_ENV = 'sandbox'
LOG_DIR = '/edx/var/logs/edx'

### Max size of asset uploads to GridFS
MAX_ASSET_UPLOAD_FILE_SIZE_IN_MB = 30

SEGMENT_IO_LMS = True
PAID_COURSE_REGISTRATION_CURRENCY = ["usd", "$"]
SEGMENT_IO_LMS = True


# Locale path
LOCALIZED_APPS = sorted([path.split("/")[-2] for path in glob(BASE_ROOT / "fun-apps/*/locale")])
LOCALE_PATHS = tuple(
    [BASE_ROOT / "fun-apps" / app / "locale" for app in LOCALIZED_APPS] +
    [
        BASE_ROOT / 'themes/fun/locale',
        BASE_ROOT / 'edx-platform/conf/locale',
        BASE_ROOT / 'venvs/edxapp/lib/python2.7/site-packages/django_countries/locale',    # this should not be required
    ]
)

# Custom password policy will be activated by FEATURES['ENFORCE_PASSWORD_POLICY'] = True
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 30
PASSWORD_COMPLEXITY = {
      'UPPER' : 1,
      'LOWER' : 1,
      'DIGITS': 1
}


from xmodule.modulestore import prefer_xmodules
XBLOCK_SELECT_FUNCTION = prefer_xmodules

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'infrasmtp02.cines.fr'   # we will use the new smtp for transactional emails on all instances

BULK_SMTP_SERVER = 'smtpmooc.cines.fr'  # old server will only be used for bulk email on brick lms
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
        "VMEM": 50*1000*1000,
    },
    "python_bin": "",
    "user": "sandbox"
}

CACHES = {
    "celery": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "util.memcache.safe_key",
        "KEY_PREFIX": "integration_celery",
        "LOCATION": [
            "localhost:11211"
        ]
    },
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "util.memcache.safe_key",
        "KEY_PREFIX": "sandbox_default",
        "LOCATION": [
            "localhost:11211"
        ]
    },
    "general": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "util.memcache.safe_key",
        "KEY_PREFIX": "sandbox_general",
        "LOCATION": [
            "localhost:11211"
        ]
    },
    "mongo_metadata_inheritance": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "util.memcache.safe_key",
        "KEY_PREFIX": "integration_mongo_metadata_inheritance",
        "LOCATION": [
            "localhost:11211"
        ]
    },
    "staticfiles": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "util.memcache.safe_key",
        "KEY_PREFIX": "integration_static_files",
        "LOCATION": [
            "localhost:11211"
        ]
    }
}

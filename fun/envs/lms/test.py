from .dev import *

ENVIRONMENT = 'test'

############# Disable useless logging
import logging
logging.getLogger("audit").setLevel(logging.WARN)
logging.getLogger("django_comment_client.utils").setLevel(logging.WARN)
logging.getLogger("factory").setLevel(logging.WARN)
logging.getLogger("raven.contrib.django.client.DjangoClient").setLevel(logging.WARN)
logging.getLogger('instructor_task.api_helper').setLevel(logging.ERROR)
logging.getLogger('instructor_task.tasks_helper').setLevel(logging.ERROR)
logging.getLogger('xmodule.modulestore.django').setLevel(logging.ERROR)

########### Imported from edx-platform/lms/envs/test.py
from path import path

SOUTH_TESTS_MIGRATE = False  # To disable migrations and use syncdb instead
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--id-file', REPO_ROOT / '.testids' / 'lms' / 'noseids',
    '--xunit-file', REPO_ROOT / 'reports' / 'lms' / 'nosetests.xml',
    '--nologcapture',
]
TEST_ROOT = path("test_root")
COMMON_TEST_DATA_ROOT = COMMON_ROOT / "test" / "data"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': TEST_ROOT / 'db' / 'fun.db'
    },

}

################# mongodb
MONGO_PORT_NUM = int(os.environ.get('EDXAPP_TEST_MONGO_PORT', '27017'))
MONGO_HOST = os.environ.get('EDXAPP_TEST_MONGO_HOST', 'localhost')
CONTENTSTORE = {
    'ENGINE': 'xmodule.contentstore.mongo.MongoContentStore',
    'DOC_STORE_CONFIG': {
        'host': MONGO_HOST,
        'db': 'xcontent',
        'port': MONGO_PORT_NUM,
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
STATICFILES_STORAGE='pipeline.storage.NonPackagingPipelineStorage'
PIPELINE_ENABLED=False

################ Disable Django debug toolbar
INSTALLED_APPS = tuple([app for app in INSTALLED_APPS if app not in DEBUG_TOOLBAR_INSTALLED_APPS])
MIDDLEWARE_CLASSES = tuple([m for m in MIDDLEWARE_CLASSES if m not in DEBUG_TOOLBAR_MIDDLEWARE_CLASSES])

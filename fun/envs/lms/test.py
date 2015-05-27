from .dev import *

ENVIRONMENT = 'test'

############ If you modify settings below this line don't forget to modify them both in lms/test.py and cms/test.py
from .. import test
from path import path

SOUTH_TESTS_MIGRATE = False  # To disable migrations and use syncdb instead
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = test.nose_args(REPO_ROOT, 'lms')

TEST_ROOT = path("test_root")
COMMON_TEST_DATA_ROOT = COMMON_ROOT / "test" / "data"
DATABASES = test.databases(TEST_ROOT)

################# mongodb
MONGO_PORT_NUM = int(os.environ.get('EDXAPP_TEST_MONGO_PORT', '27017'))
MONGO_HOST = os.environ.get('EDXAPP_TEST_MONGO_HOST', 'localhost')
CONTENTSTORE = test.contentstore(MONGO_HOST, MONGO_PORT_NUM)

PASSWORD_HASHERS = test.password_hashers
STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'
PIPELINE_ENABLED = False

CACHES.update(test.caches)
################ Disable Django debug toolbar
INSTALLED_APPS = tuple([app for app in INSTALLED_APPS if app not in DEBUG_TOOLBAR_INSTALLED_APPS])
MIDDLEWARE_CLASSES = tuple([m for m in MIDDLEWARE_CLASSES if m not in DEBUG_TOOLBAR_MIDDLEWARE_CLASSES])

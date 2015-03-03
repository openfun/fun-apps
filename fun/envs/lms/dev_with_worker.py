from .dev import *

################################# CELERY ######################################
# See edx-platform/lms/envs/dev_with_worker.py
# All you have to do is start a celery worker with:
#   ./manage.py lms --settings=fun.lms_dev_with_worker celery worker
CELERY_ALWAYS_EAGER = False
BROKER_URL = 'django://'
INSTALLED_APPS += ('djcelery.transport', )
CELERY_RESULT_BACKEND = 'database'
DJKOMBU_POLLING_INTERVAL = 1.0
MIDDLEWARE_CLASSES = tuple(
    c for c in MIDDLEWARE_CLASSES
    if c != 'django.middleware.transaction.TransactionMiddleware')


# -*- coding: utf-8 -*-
"""
Common settings for LMS & CMS developpement environments
"""

ENVIRONMENT = 'dev'

CMS_BASE = 'localhost:9001'  # Studio web address
LMS_BASE = 'localhost:9000'  # LMS web address

PREVIEW_LMS_BASE = LMS_BASE

MEDIA_ROOT = "/edx/var/edxapp/uploads"

# do not log to sentry in dev
RAVEN_CONFIG = {
    'dsn': '',
}

DEBUG = True
TEMPLATE_DEBUG = True

# By default don't use a worker, execute tasks as if they were local functions
CELERY_ALWAYS_EAGER = True

################################ LOGGERS ######################################

import logging

# Disable noisy loggers
for pkg_name in ['track.contexts', 'track.middleware', 'dd.dogapi']:
    logging.getLogger(pkg_name).setLevel(logging.CRITICAL)

################################ EMAIL ########################################

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

################################ DEBUG TOOLBAR ################################

DEBUG_TOOLBAR_INSTALLED_APPS = ('debug_toolbar', 'django_extensions',)
DEBUG_TOOLBAR_MIDDLEWARE_CLASSES = (
    'django_comment_client.utils.QueryCountDebugMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',

    #  Enabling the profiler has a weird bug as of django-debug-toolbar==0.9.4 and
    #  Django=1.3.1/1.4 where requests to views get duplicated (your method gets
    #  hit twice). So you can uncomment when you need to diagnose performance
    #  problems, but you shouldn't leave it on.
    #  'debug_toolbar.panels.profiling.ProfilingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': lambda _: True,
}

########################### PIPELINE #################################

PIPELINE_SASS_ARGUMENTS = '--debug-info --require {proj_dir}/static/sass/bourbon/lib/bourbon.rb'

########################### DEBUG #################################
TEMPLATE_STRING_IS_INVALID = "__INVALID__"

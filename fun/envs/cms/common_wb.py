# -*- coding: utf-8 -*-

from cms.envs.aws import *  # pylint: disable=wildcard-import, unused-wildcard-import
from fun.envs.common_wb import *  # pylint: disable=wildcard-import, unused-wildcard-import

INSTALLED_APPS += (
    'fun',
    'videoproviders',
    'teachers',
    'courses',
    'haystack',
    'universities',

    'easy_thumbnails',
    'ckeditor',
    'selftest',
#    'password_container',
    'raven.contrib.django.raven_compat',
#    'edx_gea'
)


ROOT_URLCONF = 'fun.cms.urls'

update_logging_config(LOGGING)

# add 'theme/cms/templates' directory to MAKO template finder to override some CMS templates...
MAKO_TEMPLATES['main'].insert(0, ENV_ROOT / 'fun-apps/fun/templates/cms')



# Allow all courses to use advanced components
FEATURES['ALLOW_ALL_ADVANCED_COMPONENTS'] = True
FEATURES['AUTH_USE_OPENID_PROVIDER'] = True
FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = False
FEATURES['ADVANCED_SECURITY'] = False
FEATURES['CERTIFICATES_ENABLED'] = True
FEATURES['CERTIFICATES_HTML_VIEW'] = True
# restrain user who can create course in studio to granted ones in CourseCreator table
FEATURES['ENABLE_CREATOR_GROUP'] = True
FEATURES['ENABLE_DISCUSSION_SERVICE'] = True
FEATURES['ENABLE_DJANGO_ADMIN_SITE'] = True
FEATURES['ENABLE_INSTRUCTOR_ANALYTICS'] = True
FEATURES['ENABLE_MAX_FAILED_LOGIN_ATTEMPTS'] = False
FEATURES['ENABLE_S3_GRADE_DOWNLOADS'] = True
FEATURES['ENFORCE_PASSWORD_POLICY'] = True
FEATURES['IS_EDX_DOMAIN'] = True  # used to display Edx Studio logo, see edx-platform/cms/templates/widgets/header.html
FEATURES['SUBDOMAIN_BRANDING'] = False
FEATURES['SUBDOMAIN_COURSE_LISTINGS'] = False
#FEATURES['USE_CUSTOM_THEME'] = False

# index courseware content in 'courseware_index' and course meta information in
# 'course_info' after every modification in studio
FEATURES['ENABLE_COURSEWARE_INDEX'] = True
FEATURES['REQUIRE_COURSE_EMAIL_AUTH'] = True


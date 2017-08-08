# -*- coding: utf-8 -*-

from xmodule.modulestore.modulestore_settings import update_module_store_settings
from lms.envs.aws import *  # pylint: disable=wildcard-import, unused-wildcard-import
from ..common import *  # pylint: disable=wildcard-import, unused-wildcard-import

INSTALLED_APPS += (
    'rest_framework.authtoken',

    'backoffice',
    'fun',
    'funsite',
    'fun_api',
    'fun_certificates',
    'fun_instructor',
    'contact',
    'course_dashboard',
    'courses',
    'courses_api',
    'course_pages',
    'newsfeed',
    'universities',
    'universities_api',
    'videoproviders',

    'haystack',
    'easy_thumbnails',
    'bootstrapform',
    'ckeditor',
    'raven.contrib.django.raven_compat',
    'pure_pagination',

    'payment',
    'payment_api',

    'forum_contributors',
    'selftest',
    'password_container',  # this is an xblock we add to applications to allow syncdb of its models
    'teachers',
    'faq',
    'edx_gea',
)
INSTALLED_APPS += get_proctoru_app_if_available()

ROOT_URLCONF = 'fun.lms.urls'

update_logging_config(LOGGING)

# Disable S3 file storage
del DEFAULT_FILE_STORAGE

# those values also have to be in env.json file,
# because pavlib.utils.envs reads it to build asset's preprocessing commands
FEATURES['ENABLE_MKTG_SITE'] = False

SITE_NAME = LMS_BASE


MIDDLEWARE_CLASSES += LEGAL_ACCEPTANCE_MIDDLEWARE

# MKTG_URL_LINK_MAP links are named url reverses belonging to Django project
# (also see MKTG_URLS in cms.py)
MKTG_URL_LINK_MAP = {
    "ABOUT": "about",
    "HONOR": "honor",
    "HOW-IT-WORKS": "how-it-works",
    "TOS": "tos",
    "FAQ": None,
    "PRIVACY": "privacy",
    "CONTACT": None,
    "UNSUPPORTED-BROWSER": "unsupported-browser",
    "LICENSES": "licenses",
    "LEGAL": "legal",
    "COPYRIGHTS": None,
    "ROOT": 'root',
    'COURSES': 'fun-courses:index',
}
FUN_MKTG_URLS = {}

FEATURES['ACCESS_REQUIRE_STAFF_FOR_COURSE'] = True  # hide spocs from course list
FEATURES['ALLOW_COURSE_STAFF_GRADE_DOWNLOADS'] = True
FEATURES['AUTH_USE_OPENID_PROVIDER'] = True
FEATURES['ADVANCED_SECURITY'] = False
FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = False
FEATURES['CERTIFICATES_ENABLED'] = True
FEATURES['CERTIFICATES_HTML_VIEW'] = True
FEATURES['ENABLE_COURSEWARE_INDEX'] = False
FEATURES['ENABLE_DISCUSSION_SERVICE'] = True
FEATURES['ENABLE_DJANGO_ADMIN_SITE'] = True
FEATURES['ENABLE_INSTRUCTOR_ANALYTICS'] = False
FEATURES['ENABLE_MAX_FAILED_LOGIN_ATTEMPTS'] = False
FEATURES['ENABLE_S3_GRADE_DOWNLOADS'] = True
FEATURES['PREVIEW_LMS_BASE'] = PREVIEW_LMS_BASE
FEATURES['SUBDOMAIN_BRANDING'] = False
FEATURES['SUBDOMAIN_COURSE_LISTINGS'] = False
FEATURES['ENFORCE_PASSWORD_POLICY'] = True
FEATURES['ENABLE_CONTENT_LIBRARIES'] = True

TEMPLATES[0]['OPTIONS']['context_processors'] += ('fun.context_processor.fun_settings',)

# Add FUN applications templates directories to MAKO template finder before edX's ones
MAKO_TEMPLATES['main'] = [
    FUN_BASE_ROOT / 'funsite/templates/lms',   # overrides template in edx-platform/lms/templates
    FUN_BASE_ROOT / 'funsite/templates',
    FUN_BASE_ROOT / 'course_pages/templates',
    FUN_BASE_ROOT / 'payment/templates',
    FUN_BASE_ROOT / 'course_dashboard/templates',
    FUN_BASE_ROOT / 'newsfeed/templates',
    FUN_BASE_ROOT / 'fun_certificates/templates',
] + MAKO_TEMPLATES['main']

# Add funsite templates directory to Django templates finder.
TEMPLATES[0]['DIRS'].insert(0, FUN_BASE_ROOT / 'funsite/templates/lms')

# Enable legal page
MKTG_URL_LINK_MAP['LEGAL'] = 'legal'

# Allow sending bulk e-mails for all courses
FEATURES['REQUIRE_COURSE_EMAIL_AUTH'] = False

# Access to sysadmin view (users, courses information. User has to be staff, see navigation.html)
FEATURES['ENABLE_SYSADMIN_DASHBOARD'] = False

# Registration form fields ('required', 'optional', 'hidden')
REGISTRATION_EXTRA_FIELDS = {
    'level_of_education': 'optional',
    'gender': 'optional',
    'year_of_birth': 'optional',
    'mailing_address': 'optional',
    'goals': 'optional',
    'honor_code': 'required',
    'city': 'required',
    'country': 'required',
}

SITE_VARIANT = 'lms'

FUN_SMALL_LOGO_RELATIVE_PATH = 'funsite/images/logos/funmooc173.png'
FUN_BIG_LOGO_RELATIVE_PATH = 'funsite/images/logos/funmoocfp.png'

# Certificates related settings
CERTIFICATE_BASE_URL = '/attestations/'
CERTIFICATES_DIRECTORY = '/edx/var/edxapp/attestations/'
FUN_LOGO_PATH = FUN_BASE_ROOT / 'funsite/static' / FUN_BIG_LOGO_RELATIVE_PATH
FUN_ATTESTATION_LOGO_PATH = FUN_BASE_ROOT / 'funsite/static' / 'funsite/images/logos/funmoocattest.png'
STUDENT_NAME_FOR_TEST_CERTIFICATE = 'Test User'

# Grades related settings
GRADES_DOWNLOAD = {
    'STORAGE_TYPE': 'localfs',
    'BUCKET': 'edx-grades',
    'ROOT_PATH': '/edx/var/edxapp/grades',
}
GRADES_DOWNLOAD_ROUTING_KEY = None


# Our new home page is so shiny and chrome that users must see it more often
FEATURES['ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER'] = False

# used by pure-pagination app, https://github.com/jamespacileo/django-pure-pagination
# for information about the constants :
# https://camo.githubusercontent.com/51defa6771f5db2826a1869eca7bed82d9fb3120/687474703a2f2f692e696d6775722e636f6d2f4c437172742e676966
PAGINATION_SETTINGS = {
    # same formatting as in github issues, seems to be sane.
    'PAGE_RANGE_DISPLAYED': 4,
    'MARGIN_PAGES_DISPLAYED': 2,
}

NUMBER_DAYS_TOO_LATE = 31

# Default visibility of student's profile to other students
ACCOUNT_VISIBILITY_CONFIGURATION["default_visibility"] = "private"

# easy-thumbnails
#SOUTH_MIGRATION_MODULES['easy_thumbnails'] = 'easy_thumbnails.south_migrations'


# Add our v3 CSS and JS files to assets compilation pipeline to make them available in courseware.
# On FUN v3 frontend, which do not use edX's templates, those files are loaded
# by funsite/templates/funsite/parts/base.html and css/lms-main.css

PIPELINE_CSS['style-vendor']['source_filenames'].append('fun/css/cookie-banner.css')
PIPELINE_CSS['style-vendor']['source_filenames'].append('funsite/css/header.css')
PIPELINE_CSS['style-vendor']['source_filenames'].append('funsite/css/footer.css')

#  can't find any common group
for group in ['base_vendor', 'main_vendor']:
    PIPELINE_JS[group]['source_filenames'].append('funsite/js/header.js')
    PIPELINE_JS[group]['source_filenames'].append('fun/js/cookie-banner.js')

FEATURES['ENABLE_DASHBOARD_SEARCH'] = True  # display a search box in student's dashboard to search in courses he is enrolled in.
FEATURES['ENABLE_COURSE_DISCOVERY'] = False  # display a search box and enable Backbone app on edX's course liste page which we do not use.

# Payment
FEATURES["ENABLE_OAUTH2_PROVIDER"] = True
FEATURES['ENABLE_PAYMENT_FAKE'] = True
FEATURES["ENABLE_CREDIT_API"] = True
FEATURES["ENABLE_CREDIT_ELIGIBILITY"] = True
FEATURES["ENABLE_MOBILE_REST_API"] = True
FEATURES['ENABLE_COMBINED_LOGIN_REGISTRATION'] = False

PAID_COURSE_REGISTRATION_CURRENCY = ["EUR", "€"]

EDX_API_KEY = 'test'

ECOMMERCE_API_SIGNING_KEY = 'test'
ECOMMERCE_API_URL = "http://localhost:8080/api/v2/"
ECOMMERCE_PUBLIC_URL_ROOT = "http://localhost:8080/"
ECOMMERCE_NOTIFICATION_URL = 'http://localhost:8080/payment/paybox/notify/'
ECOMMERCE_SERVICE_WORKER_USERNAME = 'ecommerce_worker'

JWT_ISSUER = "http://localhost:8000/oauth2"
JWT_EXPIRATION = 30

OAUTH_ENFORCE_SECURE = False
OAUTH_OIDC_ISSUER = "http://localhost:8000/oauth2"

# Append fun header script to verification pages
# DOGWOOD: probablement plus nécessaire
# PIPELINE_JS['rwd_header']['source_filenames'].append('funsite/js/header.js')

# A user is verified if he has an approved SoftwareSecurePhotoVerification entry
# this setting will create a dummy SoftwareSecurePhotoVerification for user in paybox success callback view
# I think it's better to create a dummy one than to remove verifying process in edX
FUN_ECOMMERCE_DEBUG_NO_NOTIFICATION = False

ANALYTICS_DASHBOARD_URL = False  # when True this setting add a link in instructor dashbord to analytics insigt service

# We move split mongo store at the top of store lists to make it the
# default one. Note that the 'modulestore' app makes split mongo
# available even if you have not define it in your settings.
update_module_store_settings(MODULESTORE, default_store='split')
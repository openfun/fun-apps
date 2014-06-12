# Xiti
XITI_ENABLED = True
XITI_XTN2 = "101"
# Note: XITI_JS_URL has been changed! Old value commented...
# XITI_JS_URL = "/static/themes/fun/js/vendor/xtcore.5c15ffd8e0b9.js"
XITI_JS_URL = "/static/themes/fun/js/vendor/xtcore.js"
XITI_XTSITE = "530632"
XITI_XTSD = "https://logs1279"

# Medias
MEDIA_URL = "/uploads/"

# Add the fun-apps repo to sys.path:
import sys
sys.path.append('/edx/app/edxapp/fun-apps')

# Add the universities app to the list of installed apps
from devstack import INSTALLED_APPS
INSTALLED_APPS += ('universities', )

# Use a FUN-specific root urlconf module
ROOT_URLCONF = 'fun.lms.urls'

# Locale path
LOCALE_PATHS = (
  '/edx/app/edxapp/fun-apps/locale',
  '/edx/app/edxapp/edx-platform/conf/locale',
)

# Enable admin site for university app
from devstack import FEATURES
FEATURES['ENABLE_DJANGO_ADMIN_SITE'] = True

# Enable help and legal pages
from aws import MKTG_URL_LINK_MAP
MKTG_URL_LINK_MAP['HELP'] = 'help'
MKTG_URL_LINK_MAP['LEGAL'] = 'legal'

# Contact form
INSTALLED_APPS += ('contact', )

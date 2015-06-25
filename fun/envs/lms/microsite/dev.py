# -*- coding: utf-8 -*-

from ..dev import *
from .common import *

MICROSITE_CONFIGURATION = get_microsite_configuration("localhost")

FEATURES['USE_MICROSITES'] = True

FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = True

# There are 2 ways to customize Edx font-end: The "Stanford Theming" way and the Microsite way.
# Here we are using microsites, so we disable the "Custom Theme" feature.
THEME_NAME = ""
FEATURES['USE_CUSTOM_THEME'] = False
FEATURES['ENABLE_MKTG_SITE'] = False

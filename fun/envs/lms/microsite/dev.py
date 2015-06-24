# -*- coding: utf-8 -*-

from ..dev import *
from .common import *

MICROSITE_CONFIGURATION = get_microsite_configuration("localhost")

PLATFORM_NAME = ""  # void constant which should be set to current microsite but is not.
THEME_NAME = ""
patch_features_for_microsites(FEATURES)

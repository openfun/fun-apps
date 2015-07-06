# -*- coding: utf-8 -*-

import mock
import unittest

from django.conf import settings
import fun.utils

def skipUnlessCms(func):
    return unittest.skipUnless(fun.utils.is_cms_running(), 'Test only valid in cms')(func)

def skipUnlessLms(func):
    return unittest.skipUnless(fun.utils.is_lms_running(), 'Test only valid in lms')(func)

### Microsite test settings

def fake_microsite_get_value(name, default=None):
    """
    Create a fake microsite site name.
    """
    return settings.FAKE_MICROSITE.get(name, default)

def setMicrositeTestSettings(microsite_settings=None):
    """Decorator used to run test with microsite configuration.

    We patch microsite.get_value function, used to get the microsite configuration from the current thread.
    We patch the setting USE_MICROSITES, which activates the microsite functionality.
    """
    def wrapper(test_func):

        fake_settings = microsite_settings or settings.FAKE_MICROSITE

        test_func = mock.patch("microsite_configuration.microsite.get_value", fake_settings.get)(test_func)
        return mock.patch.dict(settings.FEATURES, {'USE_MICROSITES' : True, 'USE_CUSTOM_THEME' : False})(test_func)
    return wrapper

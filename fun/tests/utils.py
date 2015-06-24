import mock
import unittest

from django.conf import settings
from django.test.utils import override_settings

def skipUnlessCms(func):
    # TODO should we use SERVICE_VARIANT setting instead?
    return unittest.skipUnless(settings.ROOT_URLCONF == 'fun.cms.urls', 'Test only valid in cms')(func)

def skipUnlessLms(func):
    return unittest.skipUnless(settings.ROOT_URLCONF == 'fun.lms.urls', 'Test only valid in lms')(func)


### Microsite test settings

def fake_microsite_get_value(name, default=None):
    """
    Create a fake microsite site name.
    """
    return settings.FAKE_MICROSITE.get(name, default)

def setMicrositeTestSettings(test_func):
    """Decorator used to run test with microsite configuration.

    We patch microsite.get_value function, used to get the microsite configuration from the current thread.
    We patch the setting USE_MICROSITES, which activates the microsite functionality.
    """
    test_func = mock.patch("microsite_configuration.microsite.get_value", fake_microsite_get_value)(test_func)
    return mock.patch.dict(settings.FEATURES, {'USE_MICROSITES' : True, 'USE_CUSTOM_THEME' : False})(test_func)

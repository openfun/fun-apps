import unittest

from django.conf import settings

def skipUnlessCms(func):
    # TODO should we use SERVICE_VARIANT setting instead?
    return unittest.skipUnless(settings.ROOT_URLCONF == 'fun.cms.urls', 'Test only valid in cms')(func)

def skipUnlessLms(func):
    return unittest.skipUnless(settings.ROOT_URLCONF == 'fun.lms.urls', 'Test only valid in lms')(func)

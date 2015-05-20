from unittest import skipUnless

from django.conf import settings

def skipUnlessCms(func):
    return skipUnless(settings.ROOT_URLCONF == 'fun.cms.urls', 'Test only valid in cms')(func)

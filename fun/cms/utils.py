from unittest import skipUnless

from django.conf import settings

def skipUnlessCms(func):
    skipUnless(settings.ROOT_URLCONF == 'fun.cms.urls', 'Test only valid in cms')(func)
    return func

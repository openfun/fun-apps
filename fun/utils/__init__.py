from django.conf import settings

def is_cms_running():
    """Return True if we are running the cms service variant"""
    return settings.ROOT_URLCONF == 'fun.cms.urls'

def is_lms_running():
    """Return True if we are running the lms service variant"""
    return settings.ROOT_URLCONF == 'fun.lms.urls'

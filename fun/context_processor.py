# -*- coding: utf-8 -*-

from django.conf import settings

from microsite_configuration import microsite


def fun_settings(request):
    """Add ENVIRONMENT name (Brick, Ketch, dev) to template context when in backoffice application."""
    context = {}
    if request.path.startswith('/backoffice/'):
        context['ENVIRONMENT'] = settings.ENVIRONMENT
        context['IS_WHITEBRAND'] = getattr(settings, 'IS_WHITEBRAND', False)

        if settings.FEATURES['USE_MICROSITES']:
            context['USE_MICROSITE'] = settings.FEATURES['USE_MICROSITES']
            context['MICROSITE_SITENAME'] = microsite.get_value('SITE_NAME')
            context['MICROSITE_PLATFORM'] = microsite.get_value('platform_name')
    return context

# -*- coding: utf-8 -*-

from django.conf import settings


def fun_settings(request):
    """Add ENVIRONMENT name (Brick, Ketch, dev) to template context when in backoffice application."""
    context = {}
    if request.path.startswith('/backoffice/'):
        context['ENVIRONMENT'] = settings.ENVIRONMENT
    return context

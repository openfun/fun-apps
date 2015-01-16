# -*- coding: utf-8 -*-

from django.conf import settings


def fun_settings(request):
    """Add ENVIRONEMENT name (Brick, Ketch, dev) to template context when in backoffice application."""
    if request.path.startswith('/backoffice/'):
        context = {
            'ENVIRONEMENT': settings.ENVIRONEMENT,
        }
        return context

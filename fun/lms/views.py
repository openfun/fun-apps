import re
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect


def richie(request, redirect_to):
    """Extract params from route to redirect to the right Richie view"""
    if (getattr(settings, "PLATFORM_RICHIE_URL", None) is not None):
        return redirect("{richie_url:s}/{target:s}".format(
            richie_url=settings.PLATFORM_RICHIE_URL,
            target=redirect_to
        ))

    return redirect(reverse("dashboard"))

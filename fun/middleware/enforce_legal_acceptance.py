# _*_ coding: utf8 _*_
"""Middleware to enforce legal acceptance when new
conditions are published"""

import re

from django.conf import settings
from django.shortcuts import redirect

from payment.models import legal_acceptance

AGREEMENT_WHITELIST = map(
    re.compile,
    (
        r"""^/payment/.*""",
        r"""^/xblock/.*""",
        r"""^/account/setting.*""",
        r""".*accept.*""",
        r"""^/(news|login|contact|about|help|legal|privacy|honor|charte)/?$""",
        r""".*/login_ajax.*""",
        r"""^/static.*""",
        r""".*search.*""",
        r""".*revision.*""",
        r"""^/static/.*""",
        r"""^/api/user/.*""",
        r"""^/c4x.*""",
        r""".*logout.*$""",
        r""".*asset.*""",
        r""".*\.(png|font|html|js|css|jpeg|pdf|gif|mp4).*""",
        r"""^/?$""",
    )
)

TERMS_AND_CONDITIONS_AGREEMENT = '/payment/terms/'


def terms_accepted(func):
    """
    force redirect to acceptance of legal condition if
    latest not accepted
    redirection landing page SHOULD be set in settings
    AGREEMENT_FORM else defaults to DEFAULT_AGREEMENT_FORM
    """
    def wrapped(request, *args, **kwargs):
        if not legal_acceptance(request.user):
            return redirect(TERMS_AND_CONDITIONS_AGREEMENT, *args, **kwargs)
        else:
            return func(request, *args, **kwargs)
    return wrapped


class LegalAcceptance(object):
    def __init__(self, *a, **kw):
        self.white_list = AGREEMENT_WHITELIST

    def is_whitelisted(self, url):
        return any(wl_url.match(url) for wl_url in self.white_list)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if (
                not self.is_whitelisted(request.path_info) and \
                hasattr(request, "user") and \
                request.user.is_authenticated() and \
                # don't enforce legal acceptance when impersonating a user
                not request.user.is_masked and \
                not legal_acceptance(request.user)):
            return terms_accepted(view_func)(request, *view_args, **view_kwargs)


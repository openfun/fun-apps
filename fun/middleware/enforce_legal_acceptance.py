# _*_ coding: utf8 _*_
"""Middleware to enforce legal acceptance when new
conditions are published"""

import re

from django.shortcuts import redirect

from payment.models import legal_acceptance

AGREEMENT_WHITELIST = map(
    re.compile,
    (
        r'^/payment/.*',
        r'^/xblock/.*',
        r'^/account/setting.*',
        r'.*accept.*',
        r'^/(news|login|contact|about|help|legal|privacy|honor|charte)/?$',
        r'.*/login_ajax.*',
        r'^/static.*',
        r'.*search.*',
        r'.*revision.*',
        r'^/static/.*',
        r'^/api/.*',
        r'^/c4x.*',
        r'.*logout.*$',
        r'.*asset.*',
        r'.*\.(png|font|html|js|css|jpeg|pdf|gif|mp4).*',
        r'^/?$',
    )
)

TERMS_AND_CONDITIONS_AGREEMENT = '/payment/terms/'


def ensure_terms_accepted(func):
    """
    force redirect to acceptance of legal condition if
    latest not accepted
    """
    def wrapped(request, *args, **kwargs):
        if not legal_acceptance(request.user):
            redirect_to = '{path:s}?next={next:s}'.format(
                path=TERMS_AND_CONDITIONS_AGREEMENT,
                next=request.path
            )
            return redirect(redirect_to, *args, **kwargs)
        else:
            return func(request, *args, **kwargs)
    return wrapped


class LegalAcceptance(object):

    def is_whitelisted(self, url):
        return any(wl_url.match(url) for wl_url in AGREEMENT_WHITELIST)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # We don't redirect the current user to the legal acceptance page if:
        #   1. the current path is whitelisted,
        #   2. the current user is impersonating another user,
        #   3. the latest T&C were already accepted by the current user.
        if (
                not self.is_whitelisted(request.path_info) and
                hasattr(request, "user") and
                request.user.is_authenticated() and
                not request.user.is_masked and
                not legal_acceptance(request.user)):
            return ensure_terms_accepted(view_func)(request, *view_args, **view_kwargs)

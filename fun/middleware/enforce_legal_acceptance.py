# _*_ coding: utf8 _*_
from functools import partial

from fun.utils.views import terms_accepted
from django.conf import settings
import re

"""Middleware to enforce legal acceptance when new
conditions are published"""

DEFAULT_AGREEMENT_WHITELIST = map(
    re.compile,
    (
        """^/payment/.*""",
        """^/account/setting.*""",
        """.*accept.*""",
        """^/(news|login|contact|about|help|legal|privacy|honor|charte)/?$""",
        """.*/login_ajax.*""",
        """^/static.*""",
        """.*search.*""",
        """.*revision.*""",
        """^/static/.*""",
        """^/api/user/.*""",
        """^/c4x.*""",
        """.*logout.*$""",
        """.*asset.*""",
        """.*\.(png|font|html|js|css|jpeg|pdf|gif|mp4).*""",
        """^/?$""",
    )
)
def get(self, key, default):
    return self.key if hasattr(self, key) else default


class LegalAcceptance(object):
    def __init__(self, *a, **kw):
        self.white_list = get(settings,
            "AGREEMENT_WHITELIST",
            DEFAULT_AGREEMENT_WHITELIST
        )

    def is_whitelisted(self, url):
        return any(wl_url.match(url) for wl_url in self.white_list)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not self.is_whitelisted(request.path_info) \
            and hasattr(request, "user") \
            and request.user.is_authenticated :
            return terms_accepted(view_func)(request, *view_args, **view_kwargs)

        return None

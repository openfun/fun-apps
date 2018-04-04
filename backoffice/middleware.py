# _*_ coding: utf8 _*_
"""Disabling user impersonation on admin and backoffice paths."""

import re

from masquerade.middleware import MasqueradeMiddleware

MASQUERADE_WHITELIST = map(
    re.compile, (
        r'^/backoffice/.*',
        r'^/admin/.*',
    )
)


class PathLimitedMasqueradeMiddleware(MasqueradeMiddleware):
    """
    Same as MasqueradeMiddleware but allow whitelisting a list of url
    patterns on which masquerading should be disabled.
    """
    def process_request(self, request):
        """
        Check if the current path matches one of the patterns we want to
        exclude and don't masquerade in this case.
        """
        path = request.path_info
        if any(u.match(path) for u in MASQUERADE_WHITELIST):
            # Don't masquerade but set attributes as django-masquerade does it
            request.user.is_masked = False
            request.user.original_user = None
            return
        return super(PathLimitedMasqueradeMiddleware, self).process_request(request)

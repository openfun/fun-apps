"""Middleware to inspect authorize oauth2 request"""
import re
from urllib import quote

from django.conf import settings
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect, QueryDict
from django.utils.six.moves.urllib.parse import urlparse, urlunparse

authorize_path = re.compile(r"/oauth2/authorize/")

class Oauth2Step(object):
    """
    When Moodle initiate an Oauth2 request, the state variable in the querystring
    contains itself a querystring. On the redirect on the login page when a user is 
    not connected, Django set in a next variable the initial request path and then redirect on this
    request path once connected. But the state is unquoted and splitted in multiple variable in the querystring...
    To fix this, first we store the initial query string in the request object and then we rebuild
    the next query string by quoting once again the state to ensure it will not be split
    once redirected.
    """
   
    def process_request(self, request):
        """
        The initial querystring in store in the request to be use later
        in the process_response.
        """
        if ("state" in request.GET 
            and not request.user.is_authenticated() 
            and authorize_path.match(request.path_info)):
            request._initial_qs = request.GET.copy()

        return None
        
    def process_response(self, request, response):
        """
        If the request contains the _initial_qs property then the
        redirected url is rebuild to secure the state.
        """
        if not hasattr(request, "_initial_qs"):
            return response
        
        qs = request._initial_qs
        qs["state"] = quote(qs.get("state"))
        resolved_url = resolve_url(settings.LOGIN_URL)
        login_url_parts = list(urlparse(resolved_url))
        querystring = QueryDict(mutable=True)
        querystring["next"] = "/oauth2/authorize/?" + qs.urlencode(safe="/")
        login_url_parts[4] = querystring.urlencode(safe="/")

        return HttpResponseRedirect(urlunparse(login_url_parts))

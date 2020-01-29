# -*- coding: utf-8 -*-

from django.shortcuts import render

from edxmako.shortcuts import render_to_response


def index(request):
    """A simple view to override edX's home page."""
    return render_to_response("index.html")


def render_static_template(request, page):
    return render(request, "funsite/static_templates/%s.html" % page, {})

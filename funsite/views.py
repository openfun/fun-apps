# -*- coding: utf-8 -*-

from django.http import Http404
from django.shortcuts import render


def render_static_template(request, page):
    return render(request, 'funsite/static_templates/%s.html' % page, {})

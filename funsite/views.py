# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect


def render_static_template(request, page):

    return render(request, 'funsite/static_templates/%s.html' % page, {})

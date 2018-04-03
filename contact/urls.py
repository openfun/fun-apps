# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from contact import views

# namespace='contact'
urlpatterns = patterns('',
    url(r'^contact/?$', views.ContactView.as_view(), name="contact"),
)

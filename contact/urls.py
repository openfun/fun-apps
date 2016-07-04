# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from contact import views

# namespace='contact'
urlpatterns = patterns('',
    url(r'^contact/?$', views.ContactFormView.as_view(), name="contact"),
    url(r'^contact/sent/$', TemplateView.as_view(template_name='contact/contact_form_sent.html'), name='contact_form_sent'),
)

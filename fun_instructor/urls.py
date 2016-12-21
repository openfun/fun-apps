# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns


urlpatterns = patterns( '',
# This url overrides edx'X ajax view which populate list of grades report available to download on teacher's dashboard.
# See views.py
url(r'^list_report_downloads$',
        'fun_instructor.views.list_report_downloads', name="list_report_downloads"),)

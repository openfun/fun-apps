# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('courses.views',
    url(r'^$', 'course_index', name='fun-courses-index'),
)

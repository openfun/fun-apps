# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import courses_index, CoursesFeed


urlpatterns = patterns('',
    url(r'^$', courses_index, name='fun-courses-index'),
    url(r'^feed/$', CoursesFeed(), name='fun-courses-feed'),
)

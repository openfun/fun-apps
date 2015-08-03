# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .routers import CourseAPIRouter
from .views import courses_index, CoursesFeed


urlpatterns = patterns('',
    url(r'^$', courses_index, name='fun-courses-index'),
    url(r'^feed/$', CoursesFeed(), name='fun-courses-feed'),
)

from .api import CourseAPIView

router = CourseAPIRouter()
router.register(r'api', CourseAPIView)
urlpatterns += router.urls

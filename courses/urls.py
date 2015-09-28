# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .routers import CourseAPIRouter
from .views import courses_index, CoursesFeed


urlpatterns = patterns('',
    url(r'^$', courses_index, name='fun-courses-index'),
    url(r'^feed/$', CoursesFeed(), name='fun-courses-feed'),
)

from .api import CourseAPIViewV1, CourseAPIView

router = CourseAPIRouter()
router.register(r'api', CourseAPIViewV1)
router.register(r'api-v2', CourseAPIView)
urlpatterns += router.urls

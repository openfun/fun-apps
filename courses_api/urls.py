# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .routers import CourseAPIRouter
from .views import courses_index, CoursesFeed
from .api import CourseAPIView


urlpatterns = patterns('',
    url(r'^$', courses_index, name='index'),
    url(r'^#filter/subject/(?P<subject>.+)$', courses_index, name='filter'),
    url(r'^feed/$', CoursesFeed(), name='feed'),
)

router = CourseAPIRouter()
router.register(r'api', CourseAPIView)
urlpatterns += router.urls

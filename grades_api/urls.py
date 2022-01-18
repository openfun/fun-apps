# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url

urlpatterns = patterns(
    "grades_api.api",
    url(r'^{}/(?P<username>[\w.+-]+)/$'.format(settings.COURSE_KEY_PATTERN), 'get_student_course_grade', name="student_grade")
)
# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url, patterns

urlpatterns = patterns('backoffice.views',
    url(r'^$', 'courses_list', name='courses-list'),
    url(r'^course/{}?$'.format(settings.COURSE_KEY_PATTERN), 'course_detail', name='course-detail'),
    url(
        r'^course/submissions/{}/'.format(settings.COURSE_KEY_PATTERN),
        include('backoffice.ora2_submissions.urls', namespace="ora2-submissions")
    ),
    url(
        r'^course/certificate/{}/'.format(settings.COURSE_KEY_PATTERN),
        include('backoffice.certificate_manager.urls')
    ),
)

# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url, patterns


urlpatterns = patterns('backoffice.views',
    url(r'^$', 'courses_list', name='backoffice-courses-list'),
    url(r'^course/{}?$'.format(settings.COURSE_KEY_PATTERN), 'course_detail', name='backoffice-course-detail'),
    url(r'^course/certificate/{}?$'.format(settings.COURSE_KEY_PATTERN), 'course_certificate', name='backoffice-course-certificate'),

)

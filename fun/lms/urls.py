# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url, include, patterns
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

import openassessment.fileupload.urls

# Important: We have to import edx routes to error pages
from lms.urls import handler404, handler500 #pylint: disable=unused-import


urlpatterns = patterns('',
    (r'^', include('funsite.urls')),
    (r'^', include('contact.urls', namespace='contact')),
    (r'^payment/', include('payment.urls')),
    (r'^universities/', include('universities.urls')),
    (r'^news/', include('newsfeed.urls')),
    # as we override a theme static_page, it has to work whith and without trailing slash
    (r'^help/', include('faq.urls', namespace='faq')),
    (r'^backoffice/', include('backoffice.urls', namespace='backoffice')),

    # fun api
    (r'^fun/api/token/', include('fun_api.urls', namespace='fun-api')),
    (r'^fun/', include('courses_api.urls', namespace='fun-courses-api')),
    (r'^fun/', include('universities_api.urls', namespace='fun-universities-api')),

    # override edX's courses page to replace by FUN's one (we need to use a other route)
    (r'^cours/', include('course_pages.urls', namespace='fun-courses')),
    url(  # intercept old routes, and redirect
        r'^courses/$',
        RedirectView.as_view(url=reverse_lazy('fun-courses:index'))
    ),
                       url(r'^courses$', RedirectView.as_view(url=reverse_lazy('fun-courses:index'))),

    url(r'^courses/{}/instructor/api/forum-contributors/'.format(settings.COURSE_ID_PATTERN),
            include('forum_contributors.urls')),
    url(r'^courses/{}/fun/dashboard/'.format(settings.COURSE_ID_PATTERN),
        include('course_dashboard.urls', namespace='course-dashboard')
    ),
    url(r'^courses/fun/dashboard/', include('course_dashboard.urls_global', namespace='course-dashboard-global')),

    # Grade downloads
    url(r'^courses/{}/instructor/api/'.format(settings.COURSE_ID_PATTERN), include('fun_instructor.urls')),
    url(r'^get-grades/{}/(?P<filename>.+.csv)'.format(settings.COURSE_ID_PATTERN), 'fun_instructor.views.get_grades'),

    # Override edx-platform urls
    url(r'^blog$', handler404),
    url(r'^donate$', handler404),
    url(r'^faq$', handler404),
    url(r'^jobs$', handler404),
    url(r'^press$', handler404),
    url(r'^media-kit$', handler404),

    # Include edx-platform urls
    (r'^', include('lms.urls')),
    (r'^', include('fun.common_urls')),

    # Ora2 file upload
    url(r'^openassessment/storage', include(openassessment.fileupload.urls)),
)

# Ckeditor - Used by Univerity app
urlpatterns += (
    url(r'^ckeditor/', include('ckeditor.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

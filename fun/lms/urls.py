# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url, include, patterns
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

# Important: We have to import edx routes to error pages
from lms.urls import handler404, handler500


urlpatterns = patterns('',
    (r'^universities/', include('universities.urls')),
    (r'^contact/', include('contact.urls')),
    (r'^news/', include('newsfeed.urls')),
    (r'^backoffice/', include('backoffice.urls')),

    # override edX's courses page to replace by FUN's one (we need to use a other route)
    (r'^cours/', include('courses.urls')),
    url(  # intercept old routes, and redirect
        r'^courses/$',
        RedirectView.as_view(url=reverse_lazy('fun-courses-index'))
    ),
    url(r'^courses$', RedirectView.as_view(url=reverse_lazy('fun-courses-index'))),

    url(r'^courses/{}/instructor/api/forum-contributors/'.format(settings.COURSE_ID_PATTERN),
            include('forum_contributors.urls')),
    url(r'^courses/{}/fun/dashboard/'.format(settings.COURSE_ID_PATTERN),
        include('course_dashboard.urls', namespace='course-dashboard')
    ),

    (r'^selftest/', include('selftest.urls')),

    # Grade downloads
    url(r'^courses/{}/instructor/api/'.format(settings.COURSE_ID_PATTERN), include('fun_instructor.urls')),
    url(r'^get-grades/{}/(?P<filename>.+.csv)'.format(settings.COURSE_ID_PATTERN), 'fun_instructor.views.get_grades'),
    (r'^', include('lms.urls')),
)

# Ckeditor - Used by Univerity app
urlpatterns += (
    url(r'^ckeditor/', include('ckeditor.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


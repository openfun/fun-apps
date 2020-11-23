# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url, include, patterns
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from . import views

import openassessment.fileupload.urls

# Important: We have to import edx routes to error pages
from lms.urls import handler404, handler500  # pylint: disable=unused-import


urlpatterns = patterns('',
    # Django Masquerade urls
    (r'^', include('masquerade.urls')),

    # fun-apps urls
    (r'^', include('funsite.urls')),
    (r'^payment/', include('payment.urls', namespace="payment")),
    (r'^universities/', include('universities.urls')),
    (r'^news/', include('newsfeed.urls')),
    # this regexp catch both /help and /help/ urls
    (r'^help(/)?$', RedirectView.as_view(url='https://fun-mooc.help')),
    (r'^backoffice/', include('backoffice.urls', namespace='backoffice')),

    # fun api
    (r'^fun/api/token/', include('fun_api.urls', namespace='fun-api')),
    (r'^fun/api/payment/', include('payment_api.urls', namespace='fun-payment-api')),
    (r'^fun/', include('courses_api.urls', namespace='fun-courses-api')),
    (r'^fun/', include('universities.urls', namespace='fun-universities-api')),

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
        include('course_dashboard.urls', namespace='course-dashboard')),
    url(r'^courses/fun/dashboard/', include('course_dashboard.urls_global', namespace='course-dashboard-global')),

    # Grade downloads
    url(r'^courses/{}/instructor/api/'.format(settings.COURSE_ID_PATTERN), include('fun_instructor.urls')),
    url(r'^get-grades/{}/(?P<filename>.+.csv)'.format(settings.COURSE_ID_PATTERN), 'fun_instructor.views.get_grades'),

    # fun certificates
    (r'^', include('fun_certificates.urls')),


    # Override edx-platform hard coded marketing urls
    # See edx-platform/lms/urls.py:165
    url(r'^blog$', handler404),
    url(r'^donate$', handler404),
    url(r'^faq$', handler404),
    url(r'^jobs$', handler404),
    url(r'^press$', handler404),
    url(r'^media-kit$', handler404),
    url(r'^contact$', RedirectView.as_view(url='https://fun-mooc.help')),


    # Include edx-platform urls
    (r'^', include('lms.urls')),
    (r'^', include('fun.common_urls')),

    # Ora2 file upload
    url(r'^openassessment/storage', include(openassessment.fileupload.urls)),

    # Richie Redirect
    url(r'^richie/(?P<redirect_to>.*)$', views.richie, name="richie_gateway"),
)

# Ckeditor - Used by Univerity app
urlpatterns += (
    url(r'^ckeditor/', include('ckeditor.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

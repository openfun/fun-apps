from django.conf.urls import patterns, url


urlpatterns = patterns('universities.views',
    url(r'^$', 'university_landing', name='universities-landing'),
    url(r'^courses/(?P<slug>[-\w]+)/$', 'university_detail', name='universities-detail'),
)

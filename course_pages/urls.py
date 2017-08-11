from django.conf.urls import patterns, url

from .views import courses_index


urlpatterns = patterns('',
    url(r'^$', courses_index, name='index'),
    url(r'^#filter/subject/(?P<subject>.+)$', courses_index, name='filter'),
)

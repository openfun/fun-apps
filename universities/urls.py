
from django.conf.urls import include, patterns, url

from rest_framework.routers import DefaultRouter

from .api import UniversityAPIViewSet


urlpatterns = patterns(
    'universities.views',
    url(r'^$', 'university_landing', name='universities-landing'),
    url(r'^(?P<slug>[-\w]+)/$', 'university_detail', name='universities-detail'),
)

router = DefaultRouter()
router.register(r'api/universities', UniversityAPIViewSet, base_name='universities_api')
urlpatterns += [
    url(r'^', include(router.urls))]

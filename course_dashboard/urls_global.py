from django.conf.urls import url, patterns

urlpatterns = patterns('course_dashboard.views',
    url(r'^enrollments/$', 'global_enrollment_stats', name='enrollment-stats'),
    url(r'^$', 'global_enrollment_stats', name='home'),
)

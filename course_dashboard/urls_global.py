from django.conf.urls import url, patterns

urlpatterns = patterns('course_dashboard.views',
    url(r'^enrollments/$', 'global_enrollment_stats', name='enrollment-stats'),
    url(r'^map/$', 'global_student_map', name='student-map'),
    url(r'^$', 'global_enrollment_stats', name='home'),
)

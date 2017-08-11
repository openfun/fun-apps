from django.conf.urls import url, patterns

urlpatterns = patterns('course_dashboard.views',
    url(r'^map/$', 'global_student_map', name='student-map'),
    url(r'^$', 'global_student_map', name='home'),
)

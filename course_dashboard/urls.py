from django.conf.urls import url, patterns

urlpatterns = patterns('course_dashboard.views',
    url(r'^enrollments/$', 'enrollment_stats', name='enrollment-stats'),
    url(r'^map/$', 'student_map', name='student-map'),
    url(r'^forum/$', 'forum_activity', name='forum-activity'),
    url(r'^$', 'enrollment_stats', name='home'),
)

from django.conf.urls import url, patterns, include 

urlpatterns = patterns('course_dashboard.views',
    url(r'^enrollments/$', 'enrollment_stats', name='enrollment-stats'),
    url(r'^map/$', 'student_map', name='student-map'),
    url(r'^forum/$', 'forum_activity', name='forum-activity'),
    url(r'^problem_stats/', include('course_dashboard.problem_stats.urls',
                                           namespace='problem-stats')),
    url(r'^reports_manager/', include('course_dashboard.reports_manager.urls',
                                                           namespace='reports-manager')),
    url(r'^$', 'enrollment_stats', name='home'),
)

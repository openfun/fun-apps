from django.conf.urls import url, patterns, include

urlpatterns = patterns('course_dashboard.views',
    url(r'^forum/$', 'forum_activity', name='forum-activity'),
    url(r'^certificate_stats/', 'certificate_stats', name='certificate-stats'),
    url(r'^reports_manager/', include('course_dashboard.reports_manager.urls',
                                      namespace='reports-manager')),
    url(r'^wiki/$', 'wiki_activity', name='wiki-activity'),
    url(r'^$', 'forum_activity', name='home'),
)

from django.conf.urls import url, patterns

urlpatterns = patterns('course_dashboard.reports_manager.views',
    url(r'^dashboard/$', 'dashboard', name='dashboard'),
    url(r'^generate/(?P<problem_id>[a-z0-9]{32})/$', 'generate', name='generate'),
    url(r'^download/(?P<answers_distribution_report>.+.csv)$', 'download', name='download'),
)


from django.conf.urls import url, patterns


urlpatterns = patterns( '',
url(r'^list_report_downloads$',
        'fun_instructor.views.list_report_downloads', name="list_report_downloads"),)

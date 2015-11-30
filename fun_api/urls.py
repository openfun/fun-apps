from django.conf.urls import patterns, url


urlpatterns = patterns('fun_api.views',
    url(r'^$', 'get_token', name='fun-get-token'),
)

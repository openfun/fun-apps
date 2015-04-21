from django.conf import settings
from django.conf.urls import url, include, patterns


urlpatterns = patterns('',
    (r'^selftest/', include('selftest.urls')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

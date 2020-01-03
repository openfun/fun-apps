from django.conf import settings
from django.conf.urls import url, include, patterns


urlpatterns = []

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),

        # Fonts are loaded from /fonts/ in DEBUG mode because the loaded
        # stylesheets are not compiled/compressed.
        url(r'^(?P<path>fonts/vendor/.+)$',
            view='django.views.static.serve',
            kwargs={'document_root' : settings.STATIC_ROOT}),
    )

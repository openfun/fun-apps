from django.conf.urls import url, patterns

urlpatterns = patterns('fun.cms.views.youtube',
    url(r'^subtitles/(?P<subtitle_id>[a-zA-Z0-9.\-_]+)$', 'download_subtitle', name='download_subtitle'),
    url(r'^upload_video$', 'upload_video', name='upload_video'),
)

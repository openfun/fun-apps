from django.conf.urls import url, patterns

from videoproviders.patterns import SUBTITLE_ID_PATTERN

urlpatterns = patterns('fun.cms.views.youtube',
    url(r'^subtitles/(?P<subtitle_id>{})$'.format(SUBTITLE_ID_PATTERN),
        'download_subtitle', name='download_subtitle'),
    url(r'^upload_video$', 'upload_video', name='upload_video'),
)

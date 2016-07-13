from django.conf.urls import url, patterns

from videoproviders.patterns import SUBTITLE_ID_PATTERN, VIDEO_ID_PATTERN

def format_video_pattern(pattern):
    video = r'(?P<video_id>{})'.format(VIDEO_ID_PATTERN)
    subtitle = r'(?P<subtitle_id>{})'.format(SUBTITLE_ID_PATTERN)
    return pattern.format(video=video, subtitle=subtitle)

urlpatterns = patterns('fun.cms.views.videoupload',
    # videos
    url(format_video_pattern(r'^api/videos/{video}$'), 'video', name='video'),
    url(format_video_pattern(r'^api/videos$'), 'get_videos', name='videos'),

    # video
    url(format_video_pattern(r'^api/files/upload$'), 'file_upload_url', name='upload-url'),
    url(format_video_pattern(r'^api/video/create$'), 'create_video', name='create-video'),

    # subtitles
    # It is important that the endpoint for a single url has the same root as
    # the url for the subtitle list, for reasons inherent to
    # backbone.js.
    url(format_video_pattern(r'^api/video/{video}/subtitles$'),
        'video_subtitles', name='video-subtitles'),
    url(format_video_pattern(r'^api/video/{video}/subtitles/{subtitle}$'),
        'video_subtitle', name='video-subtitle'),

    # thumbnail
    url(format_video_pattern(r'^api/video/{video}/thumbnail$'),
        'video_update_thumbnail', name='video-update_thumbnail'),

    # dashboard
    url(format_video_pattern(r'^$'), 'home', name='home'),
)

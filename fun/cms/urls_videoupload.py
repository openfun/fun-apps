from django.conf.urls import url, patterns

def format_video_pattern(pattern):
    return pattern.format(
        video='(?P<video_id>[a-z0-9]+)',
        subtitle='(?P<subtitle_id>[a-z0-9.]+)',
    )

urlpatterns = patterns('fun.cms.views.videoupload',
    # videos
    url(format_video_pattern(r'^api/videos/(?P<video_id>[a-z0-9]+)$'), 'video', name='video'),
    url(format_video_pattern(r'^api/videos$'), 'get_videos', name='videos'),

    # video
    url(format_video_pattern(r'^api/files/upload$'), 'file_upload', name='upload-url'),
    url(format_video_pattern(r'^api/video/create$'), 'create_video', name='create-video'),
    url(format_video_pattern(r'^api/video/publish$'), 'publish_video', name='publish-video'),
    url(format_video_pattern(r'^api/video/unpublish$'), 'unpublish_video', name='unpublish-video'),

    # subtitles
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


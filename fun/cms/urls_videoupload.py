from django.conf.urls import url, patterns

def format_video_pattern(pattern):
    return pattern.format(
        video=r'(?P<video_id>[a-z0-9.\-_]+)',
        subtitle=r'(?P<subtitle_id>[a-z0-9.\-_]+)',
    )

urlpatterns = patterns('fun.cms.views.videoupload',
    # videos
    url(format_video_pattern(r'^api/videos/{video}$'), 'video', name='video'),
    url(format_video_pattern(r'^api/videos$'), 'get_videos', name='videos'),

    # video
    url(format_video_pattern(r'^api/files/upload$'), 'file_upload', name='upload-url'),
    url(format_video_pattern(r'^api/video/create$'), 'create_video', name='create-video'),
    url(format_video_pattern(r'^api/video/publish$'), 'publish_video', name='publish-video'),
    url(format_video_pattern(r'^api/video/unpublish$'), 'unpublish_video', name='unpublish-video'),

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


# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns

urlpatterns = patterns('newsfeed.views',
    url(r'^$', 'article_list', name='newsfeed-landing'),
    url(r'^preview/(?P<slug>[-\w]+)/$', 'article_list_preview', name='newsfeed-landing-preview'),
    url(r'^article/preview/(?P<slug>[-\w]+)/$', 'article_preview', name='newsfeed-article-preview'),
    url(r'^(?P<slug>[-\w]+)/$', 'article_detail', name='newsfeed-article'),
)

urlpatterns += patterns('newsfeed.views_ckeditor',
    url(r'^ckeditor/upload/$', 'ckeditor_upload', name='news-ckeditor-upload'),
    url(r'^ckeditor/browse/$', 'ckeditor_browse', name='news-ckeditor-browse'),
)

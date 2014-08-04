# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('forum_contributors.views',
    url(r'^list-special-forum-contributors$', 'list_special_forum_contributors', name='list_special_forum_contributors_url'),
    url(r'^modify-special-forum-contributors$', 'modify_special_forum_contributors', name='modify_special_forum_contributors_url'),
)

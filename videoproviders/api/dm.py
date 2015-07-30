# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _

import dailymotion

from .. import models
from .base import BaseClient, MissingCredentials, ClientError


class Client(BaseClient):
    # Warning: this is mostly NOT unit-tested code

    VIDEO_FIELDS = 'id,created_time,embed_url,status,title,thumbnail_url'
    SUBTITLE_FIELDS = 'id,language,language_label,url'
    CHANNEL = 'school'
    TAGS = [u"France Université Numérique"]

    def __init__(self, course_key_string):
        super(Client, self).__init__(course_key_string)
        self._dailymotion = None
        self._auth = None

    @property
    def dailymotion(self):
        if self._dailymotion is None:
            self._dailymotion = dailymotion.Dailymotion()
            self._dailymotion.set_grant_type(
                'password', api_key=self.auth.api_key, api_secret=self.auth.api_secret,
                info={'username': self.auth.username, 'password': self.auth.password},
                scope=['userinfo', 'manage_videos', 'manage_subtitles']
            )
            self._dailymotion._session_store.set({
                'access_token': self.auth.access_token,
                'refresh_token': self.auth.refresh_token,
                'expires': self.auth.expires_at
            })
        return self._dailymotion

    def get_auth(self):
        """Return the DailymotionAuth credentials for the course after checking their validity."""
        try:
            auth = models.DailymotionAuth.objects.get_for_course(self.course_module)
        except models.DailymotionAuth.DoesNotExist:
            raise MissingCredentials(self.org)
        if not all([auth.username, auth.password, auth.api_key, auth.api_secret]):
            raise MissingCredentials(self.org)
        return auth

    @property
    def playlist_id(self):
        """Playlist id associated to this account
        TODO"""

    def iter_videos(self):
        """Iterator over the current user's videos."""
        for result in self.iter_results("/me/videos", {'fields': self.VIDEO_FIELDS}):
            yield self.convert_result_to_video(result)

    def get_video(self, video_id):
        result = self.get("/video/{}".format(video_id), {'fields': self.VIDEO_FIELDS})
        return self.convert_result_to_video(result)

    def convert_result_to_video(self, result):
        # TODO we should probably remove some unnecessary fields here
        result['created_at'] = self.timestamp_to_str(result['created_time'])
        result['external_link'] = "http://www.dailymotion.com/video/{}".format(result['id'])
        return result

    def get_upload_url(self):
        response = self.get("/file/upload")
        if 'upload_url' not in response:
            raise ClientError(_("Could not fetch upload url"))
        return {
            'url': response['upload_url'],
            'file_parameter_name': 'file',
        }

    def update_video_title(self, video_id, title):
        return self.update_video(video_id, title=title)

    def update_video(self, video_id, **kwargs):
        """Set video attributes

        Returns:
            {
                "owner": "x1j661v",
                "id": video_id,
                "channel": None,
                "title": "My title"
            }
        """
        params = {}
        for key, value in kwargs.iteritems():
            if value is not None:
                if value == True:
                    value = "true"
                elif value == False:
                    value = "false"
                params[key] = value
        return self.post("/video/{}".format(video_id), params)

    def create_video(self, payload, title=None):
        """Create a video after it has been uploaded.

        Returns: (same as update_video)
            {
                "owner": "x1j661v",
                "id": video_id,
                "channel": None,
                "title": "My title"
            }
        """
        url = payload.get("url")
        if not url:
            raise ClientError(_("Missing url parameter"))
        params = {"url": url}
        if title:
            params["title"] = title
        return self.post("/me/videos", params)

    def publish_video(self, video_id):
        # TODO do we need to specify the title again here?
        # Set channel and tags while we are at it
        return self.update_video(
            video_id,
            published=True,
            #title=title,
            channel=self.CHANNEL,
            tags=self.TAGS,
        )

    def unpublish_video(self, video_id):
        return self.update_video(video_id, published=False)

    def delete_video(self, video_id):
        """
        Note that the video may remain in the "deleted" status for some time.
        """
        self.delete("/video/{}".format(video_id))

    def set_thumbnail(self, video_id, url):
        return self.update_video(video_id, thumbnail_url=url)

    def get_video_subtitles(self, video_id):
        return list(self.iter_results(self.video_subtitles_url(video_id),
                                      {"fields": self.SUBTITLE_FIELDS}))

    def upload_subtitle(self, video_id, file_object, language):
        subtitle_url = self.upload_file(file_object)
        self.post(
            self.video_subtitles_url(video_id),
            {'url': subtitle_url, 'language': language, 'format': 'SRT'}
        )

    def delete_video_subtitle(self, video_id, subtitle_id):
        # TODO do we really have to return something?
        return self.delete(self.video_subtitle_url(video_id, subtitle_id))

    def video_subtitles_url(self, video_id):
        return "/video/{}/subtitles".format(video_id)

    def video_subtitle_url(self, video_id, subtitle_id):
        return "/video/{}/subtitles/{}".format(video_id, subtitle_id)

    def iter_results(self, url, params):
        """Iterate over the results of a GET request"""
        page = 1
        while True:
            params['page'] = page
            results = self.get(url, params)
            for result in results["list"]:
                yield result
            page += 1
            if not results['has_more']:
                break

    def request(self, endpoint, method='GET', params=None, files=None):
        try:
            result = self.dailymotion.call(endpoint, method=method, params=params, files=files)
        except (dailymotion.DailymotionClientError, dailymotion.DailymotionApiError) as e:
            raise ClientError(e.message)

        self.auth.update_token(
            self.dailymotion._session_store.get_value("access_token"),
            self.dailymotion._session_store.get_value("refresh_token"),
            self.dailymotion._session_store.get_value("expires"),
        )
        return result

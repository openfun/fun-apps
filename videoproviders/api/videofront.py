from datetime import datetime
import logging
from time import mktime

import requests
from django.conf import settings

from fun.utils.i18n import language_name
import universities.models
from videoproviders import models
from .base import BaseClient, ClientError, MissingCredentials


logger = logging.getLogger(__name__)


class Client(BaseClient):
    VIDEOFRONT_URL = getattr(settings, 'VIDEOFRONT_URL', 'https://video.alt.openfun.fr')
    VIDEOFRONT_REQUEST_TIMEOUT_SECONDS = 10

    def __init__(self, course_key_string):
        super(Client, self).__init__(course_key_string)
        self._playlist_id = None

    @property
    def playlist_id(self):
        if self._playlist_id is None:
            try:
                course_settings = models.VideofrontCourseSettings.objects.get(course_id=self.course_id)
                self._playlist_id = course_settings.playlist_id
            except models.VideofrontCourseSettings.DoesNotExist:
                # Search for a playlist with the same name as the course id
                course_key_string = unicode(self.course_id)
                playlists = self.get(
                    'playlists/',
                    params={'name': course_key_string},
                    log_error=True
                ).json()
                if playlists:
                    self._playlist_id = playlists[0]['id']
                else:
                    # Create playlist
                    # Note that it's our job to make sure that no two playlists
                    # with the same name exist
                    playlist = self.post(
                        'playlists/',
                        data={'name': course_key_string},
                        log_error=True,
                    ).json()
                    self._playlist_id = playlist['id']
                # In both cases, store the corresponding playlist id
                course_settings, _created = models.VideofrontCourseSettings.objects.get_or_create(
                    course_id=self.course_id
                )
                course_settings.playlist_id = self._playlist_id
                course_settings.save()

        return self._playlist_id

    def convert_video_to_dict(self, video):
        processing = video['processing']
        created_at = datetime.strptime(processing['started_at'], "%Y-%m-%dT%H:%M:%SZ")
        created_at_timestamp = mktime(created_at.timetuple())

        progress = processing['progress']
        status = {
            'success': self.STATUS_READY,
            'processing': self.STATUS_PROCESSING,
            'failed': self.STATUS_ERROR,
        }.get(processing['status'], self.STATUS_PROCESSING)

        external_link = ''
        if video['formats']:
            highest_bitrate_format = max(video['formats'], key=lambda f: f['bitrate'])
            external_link = highest_bitrate_format['url']

        return {
            'id': video['id'],
            'created_at': self.timestamp_to_str(created_at_timestamp),
            'created_at_timestamp': created_at_timestamp,
            'title':  video['title'],
            'thumbnail_url': video['thumbnail'],
            'status': status,
            'encoding_progress': progress,
            # 'embed_url': ...,
            'video_sources': [
                {
                    'label': video_format['name'],
                    'res': video_format['bitrate'],
                    'url': video_format['url']
                } for video_format in video['formats']
            ],
            'external_link': external_link,
        }

    def fetch_video(self, video_id):
        response = self.get('videos/{}'.format(video_id))
        return response.json()

    def get(self, endpoint, log_error=False, **kwargs):
        return self.request(endpoint, 'GET', log_error=log_error, **kwargs)

    def post(self, endpoint, log_error=False, **kwargs):
        return self.request(endpoint, 'POST', log_error=log_error, **kwargs)

    def put(self, endpoint, log_error=False, **kwargs):
        return self.request(endpoint, 'PUT', log_error=log_error, **kwargs)

    def delete(self, endpoint, log_error=False, **kwargs):
        return self.request(endpoint, 'DELETE', log_error=log_error, **kwargs)

    def request(self, endpoint, method, log_error=False, **kwargs):
        """
        Args:
            endpoint (str)
            method (str): 'GET', 'PUT', 'POST', ...
            log_error (bool): in case of error, if this is activated, an error log will be emitted.
            **kwargs: additional arguments to be passed to the requests function
        """
        func = getattr(requests, method.lower())
        url = self.videofront_url(endpoint)

        if not kwargs.get('headers'):
            kwargs['headers'] = {}
        kwargs.setdefault('timeout', self.VIDEOFRONT_REQUEST_TIMEOUT_SECONDS)

        # Get token either from parameters or from auth attribute
        token = kwargs.pop('token', None)
        if not token:
            # Note that self.auth should not be called if the token is passed
            # in kwargs; otherwise, there is infinite recursion.
            token = self.auth
        kwargs['headers'].setdefault('Authorization', 'Token ' + token)

        response = func(url, **kwargs)
        if response.status_code >= 400:
            if response.status_code >= 500 or log_error:
                logger.error("Videofront %d eror: %s %s - %r", response.status_code, method, endpoint, response.content)
            if response.status_code >= 500:
                raise ClientError('Video provider error')
            else:
                # Error response is of the form {key: value}
                message = "\n".join([
                    "%r: %r" % (key, value)
                    for key, value in response.json().items()
                ])
                raise ClientError(message)
        return response

    def videofront_url(self, endpoint):
        return self.VIDEOFRONT_URL + '/api/v1/{endpoint}'.format(endpoint=endpoint)

    def get_video_with_subtitles(self, video_id):
        """Return a single video, identified by its id, along with the
        subtitles information. This method is used by the video xblock to fetch
        video + subtitles info in one go."""
        video = self.fetch_video(video_id)
        video_dict = self.convert_video_to_dict(video)
        video_dict['subtitles'] = [
            {
                'id': sub['id'],
                'url': sub['url'],
                'language': sub['language'],
                'language_label': language_name(sub['language']),
            }
            for sub in video['subtitles']
        ]
        return video_dict

    ####################
    # Overridden methods
    ####################

    def get_auth(self):
        """Return the authentication token for the university."""
        try:
            university = universities.models.University.objects.get(code=self.course_id.org)
        except universities.models.University.DoesNotExist:
            raise MissingCredentials(self.org)
        try:
            auth = models.VideofrontAuth.objects.get(university=university)
        except models.VideofrontAuth.DoesNotExist:
            admin_token = getattr(settings, 'VIDEOFRONT_ADMIN_TOKEN', None)
            if not admin_token:
                raise MissingCredentials(self.org)

            # Get corresponding university

            # Get or create user from API
            try:
                response = self.get('users/{}/'.format(self.org), token=admin_token)
            except ClientError:
                # Create user
                response = self.post(
                    'users/',
                    data={'username': self.org},
                    token=admin_token,
                    log_error=True
                )

            token = response.json()['token']
            auth, _created = models.VideofrontAuth.objects.get_or_create(
                university=university, token=token
            )

        if not auth.token:
            raise MissingCredentials(self.org)
        return auth.token

    def get_video(self, video_id):
        """Return a single video, identified by its id."""
        video = self.fetch_video(video_id)
        return self.convert_video_to_dict(video)

    def iter_videos(self):
        for video in self.get(
                'videos/',
                params={"playlist_id": self.playlist_id},
                log_error=True,
        ).json():
            yield self.convert_video_to_dict(video)

    def delete_video(self, video_id):
        self.delete('videos/{}'.format(video_id))

    def update_video_title(self, video_id, title):
        response = self.put(
            'videos/{}/'.format(video_id), data={'title': title},
            log_error=True,
        )
        return self.convert_video_to_dict(response.json())

    def iter_subtitles(self, video_id):
        video = self.fetch_video(video_id)
        for subtitle in video['subtitles']:
            yield {
                'id': subtitle['id'],
                'language': subtitle['language'],
                'url': subtitle['url'],
            }

    def get_upload_url(self, origin=None):
        upload_url = self.post(
            'videouploadurls/',
            data={
                'playlist': self.playlist_id,
                'origin': origin or "http://%s" % settings.CMS_BASE
            },
            log_error=True
        ).json()
        video_id = upload_url['id']
        url = self.videofront_url("videos/{}/upload/".format(video_id))
        return {
            'url': url,
            'file_parameter_name': 'file',
        }

    def create_video(self, payload, title=None):
        # This is useful for setting the video title
        video_id = payload['id']
        if title:
            self.update_video_title(video_id, title)
        return self.get_video(video_id)

    def upload_thumbnail(self, video_id, file_object):
        self.post(
            'videos/{}/thumbnail/'.format(video_id),
            files={'file': file_object},
            log_error=False,
        )
        return {}

    def upload_subtitle(self, video_id, file_object, language):
        subtitle = self.post(
            'videos/{}/subtitles/'.format(video_id),
            data={'language': language},
            files={'file': file_object},
            log_error=True,
        ).json()

        return {
            'id': subtitle['id'],
            'language': subtitle['language'],
            'url': subtitle['url'],
        }

    def delete_video_subtitle(self, video_id, subtitle_id):
        self.delete('subtitles/{}/'.format(subtitle_id))


class VideofrontError(Exception):
    pass

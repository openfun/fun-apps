# -*- coding: utf-8 -*-
from datetime import datetime
import requests

from django.utils import formats
from django.utils.translation import gettext as _

from fun.utils import get_course


class MissingCredentials(Exception):

    @property
    def verbose_message(self):
        return _(
            """There is no video storage credentials defined for this account. """
            """Please get in touch with your administrator or support team to """
            """setup the credentials for university '{}'"""
        ).format(self.message)


class ClientError(Exception):
    pass


class BaseClient(object):
    """Base class from which video provider clients all inherit."""

    def __init__(self, course_key_string):
        self.course_module = get_course(course_key_string)
        self._auth = None

    @property
    def auth(self):
        if self._auth is None:
            self._auth = self.get_auth()
        return self._auth

    @property
    def org(self):
        return self.course_id.org

    @property
    def course_id(self):
        return self.course_module.id

    def timestamp_to_str(self, timestamp):
        return formats.date_format(
            datetime.fromtimestamp(timestamp),
            "DATETIME_FORMAT"
        )

    def get_videos(self):
        """Return a list of videos for the course."""
        return list(self.iter_videos())

    def upload_thumbnail(self, video_id, file_object):
        thumbnail_url = self.upload_file(file_object)
        return self.set_thumbnail(video_id, thumbnail_url)

    def upload_file(self, file_object):
        """Upload a file to the storage service

        This can be used to store e.g: videos, subtitles or thumbnail files.

        Args:
            file_object: File-like object.

        Returns:
            url (str): url to the uploaded file.
        """
        # Get upload url
        upload_url = self.get_upload_url()

        # Store file using the obtained upload url
        upload_response = requests.post(
            upload_url['url'],
            files={upload_url['file_parameter_name']: file_object}
        )
        upload_response = upload_response.json()

        try:
            return upload_response['url']
        except KeyError:
            raise ClientError("Error in uploading file")

    def get(self, endpoint, params=None):
        return self.request(endpoint, params=params)

    def post(self, endpoint, params=None, files=None):
        return self.request(endpoint, method='POST', params=params, files=files)

    def put(self, endpoint, params=None, files=None):
        return self.request(endpoint, method='PUT', params=params, files=files)

    def delete(self, endpoint, params=None):
        return self.request(endpoint, method='DELETE', params=params)

    #################################
    # Methods to implement start here
    #################################

    def request(self, endpoint, method='GET', params=None, files=None):
        raise NotImplementedError()

    def get_auth(self):
        """Return the credentials for the course.

        Raise MissingCredentials error in case of undefined credentials.
        """
        raise NotImplementedError()

    def iter_videos(self):
        """Iterator on the videos for this course.

        Returns:
            videos (iterator): the objects yielded by this operator are dict of the form:
                {
                    'id': ...,
                    'created_at': ...,
                    'title':  ...,
                    'thumbnail_url': ...,
                    'status': ...,
                    'embed_url': ...,
                    'video_sources': [...
                        {
                            'label': ...,
                            'res': ...,
                            url: ...
                        },
                        ...
                    ],
                    'external_link': ...,
                }
        TODO: document the list of required dictionary keys. In particular: title, external_link, etc.
        """
        raise NotImplementedError()

    def get_video(self, video_id):
        """Return a single video, identified by its id."""
        raise NotImplementedError()

    def delete_video(self, video_id):
        """Delete a video

        Returns:
            None
        """
        raise NotImplementedError()

    def update_video_title(self, video_id, title):
        """Change a video title"""
        raise NotImplementedError()

    def get_upload_url(self):
        """Get a URL for uploading a video.
        Returns: {
            "url": "http...", # url on which a POST should be made
            "file_parameter_name": "path" # name of the file parameter to be sent to the url
        }
        """
        raise NotImplementedError()

    def create_video(self, payload, title=None):
        """Create a video after it has been uploaded.

        Args:
            payload (dict): data returned by the video upload call.
            title (str): Title of the video to create.
        """
        raise NotImplementedError()

    def publish_video(self, video_id):
        """Publish a video after it has been created"""
        raise NotImplementedError()

    def unpublish_video(self, video_id):
        """Unpublish a video after it has been published"""

    def set_thumbnail(self, video_id, url):
        """Set the video thumbnail

        Arguments:
            url (str): url at which the thumbnail file can be found
        """
        raise NotImplementedError()

    def get_video_subtitles(self, video_id):
        """Get the subtitles associated to a video"""
        raise NotImplementedError()

    def upload_subtitle(self, video_id, file_object, language):
        """Upload and associate a subtitle file to a video.

        Args:
            video_id (str)
            file_object (file-like object)
            language (str): 2-characters language code. E.g: 'fr', 'en'.
        Returns:
            None
        """
        raise NotImplementedError()

    def delete_video_subtitle(self, video_id, subtitle_id):
        """Delete a subtitle

        Returns:
            None
        """
        raise NotImplementedError()


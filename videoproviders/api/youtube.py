import httplib2
import mimetypes
import time

import googleapiclient.discovery
from googleapiclient.http import MediaIoBaseUpload
import oauth2client.client

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext as _

from ..models import YoutubeAuth, YoutubeCourseSettings

from .base import BaseClient, ClientError, MissingVideo, MissingCredentials

# TODO translate error messages


class Client(BaseClient):

    # In France, the Youtube category code for education is 27, as per
    # https://developers.google.com/youtube/v3/docs/videoCategories/list#try-it
    YOUTUBE_CATEGORY_ID = "27"

    FILE_PARAMETER_NAME = "path"

    def __init__(self, course_key_string):
        super(Client, self).__init__(course_key_string)
        self.course_key_string = course_key_string
        self._credentials = None
        self._playlist_id = None

    @property
    def auth(self):
        auth = super(Client, self).auth
        # Check if the access token has changed
        if auth._http.request.credentials.access_token != self.credentials.access_token:
            self.credentials.access_token = auth._http.request.credentials.access_token
            self.credentials.token_expiry = auth._http.request.credentials.token_expiry
            self.credentials.save()
        return auth

    def get_auth(self):
        google_credentials = oauth2client.client.GoogleCredentials(
            self.credentials.access_token,
            self.credentials.client_id,
            self.credentials.client_secret,
            self.credentials.refresh_token,
            self.credentials.token_expiry,
            "https://accounts.google.com/o/oauth2/token",# token URI
            None,# user agent
        )
        http_auth = google_credentials.authorize(httplib2.Http())
        client = googleapiclient.discovery.build("youtube", "v3", http=http_auth)
        return client

    @property
    def credentials(self):
        if self._credentials is None:
            try:
                self._credentials = YoutubeAuth.objects.filter(university__code=self.org)[0]
            except IndexError:
                raise MissingCredentials(self.org)
        return self._credentials

    @property
    def playlist_id(self):
        if self._playlist_id is None:
            try:
                # Read from YoutubeCourseSettings object
                course_settings = YoutubeCourseSettings.objects.get(course_id=self.course_id)
            except YoutubeCourseSettings.DoesNotExist:
                playlist_id = self.find_or_create_playlist(self.course_key_string)

                # Update settings
                course_settings, _created = YoutubeCourseSettings.objects.get_or_create(course_id=self.course_id)
                if not course_settings.playlist_id:
                    course_settings.playlist_id = playlist_id
                    course_settings.save()
            self._playlist_id = course_settings.playlist_id
        return self._playlist_id

    def find_or_create_playlist(self, title):
        """Find a playlist with the given title; create it if it does not exist.

        Return:
            playlist_id (str)
        """
        playlist_id = self.find_playlist(title)
        if playlist_id is not None:
            return playlist_id

        return self.create_playlist(title)

    def find_playlist(self, title):
        """
        List all user playlists to find the one with the correct title (equal to
        the course key string).
        Return:
            playlist_id (str) or None
        """
        for playlist in iter_page_items(
                self.auth.playlists().list,
                part="id,snippet", mine=True,
                maxResults=50
        ):
            if playlist["snippet"]["title"] == title:
                return playlist["id"]
        return None

    def create_playlist(self, title):
        """
        Create an unlisted playlist with the provided title.

        Return:
            playlist_id (str)
        """
        playlist = self.auth.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {"title": title},
                "status": {"privacyStatus": "unlisted"}
            }
        ).execute()
        return playlist["id"]

    def convert_subtitle_to_dict(self, subtitle):
        # Note that this will work only in the CMS. Subtitle download is only supported in the CMS.
        subtitle_id = subtitle['id']
        return {
            "id": subtitle_id,
            "language": subtitle["snippet"]["language"],
            "url": "//" + settings.CMS_BASE + reverse(
                "youtube:download_subtitle",
                kwargs={'subtitle_id': subtitle_id, 'course_key_string': self.course_key_string}
            )
        }

    def iter_selected_videos(self, video_ids):
        if not video_ids:
            raise ValueError("Empty video_ids")
        # We cannot make a request with too many video IDs, otherwise the http
        # url becomes too long, or the request is invalid. So we need to split
        # the video_ids in smaller subarrrays.
        index_offset = 10
        for start_index in range(0, len(video_ids), index_offset):
            video_ids_partial = video_ids[start_index:start_index+index_offset]
            for video in iter_page_items(
                    self.auth.videos().list,
                    part="id,snippet,status",
                    id=','.join(video_ids_partial)
            ):
                created_at_datetime = parse_datetime(video['snippet']['publishedAt'])
                created_at_timestamp = time.mktime(created_at_datetime.timetuple())
                created_at = self.timestamp_to_str(created_at_timestamp)

                upload_status = video['status']['uploadStatus']
                status = self.STATUS_PUBLISHED if upload_status == 'processed' else self.STATUS_PROCESSING
                video_id = video['id']
                yield {
                    'id': video_id,
                    'created_at': created_at,
                    # TODO we should modify the base class to insert the timestamp automatically
                    'created_at_timestamp': created_at_timestamp,
                    'title':  video['snippet']['title'],
                    'thumbnail_url': "",
                    'status': status,
                    #'encoding_progress': "TODO",
                    'embed_url': "https://www.youtube.com/embed/{}".format(video_id),
                    'video_sources': [],
                    'external_link': "https://www.youtube.com/watch?v={}".format(video_id),
                }

    ####################
    # Overridden methods
    ####################
    def iter_videos(self):
        """Iterate on course playlist videos"""
        playlist_items = iter_page_items(
                self.auth.playlistItems().list,
                part="id,snippet",
                playlistId=self.playlist_id,
                maxResults=50
        )
        video_ids = []
        for playlist_item in playlist_items:
            resource = playlist_item['snippet']['resourceId']
            if resource['kind'] == 'youtube#video':
                video_id = resource['videoId']
                # Playlists may contain videos multiple times
                if video_id not in video_ids:
                    video_ids.append(video_id)
        if video_ids:
            for video in self.iter_selected_videos(video_ids):
                yield video

    def request(self, endpoint, method='GET', params=None, files=None, headers=None):#pylint: disable=too-many-arguments
        # This method is not needed for this backend. Note that once the
        # libcast backend has been removed, we should be able to delete this
        # method and the get,post,put,delete,safe_* methods from this class and
        # its base class.
        raise NotImplementedError()

    def get_video(self, video_id):
        videos = self.iter_selected_videos([video_id])
        for video in videos:
            return video
        raise MissingVideo()

    def delete_video(self, video_id):
        # IMPORTANT NOTE this allows just any course staff to delete any video
        # from any course. Which is bad, obviously...
        self.auth.videos().delete(id=video_id).execute()

    def update_video_title(self, video_id, title):
        if len(title) > 100:
            raise ClientError(
                _(
                    "Maximum supported video title length is 100 characters. "
                    "Cannot set title with {count} characters"
                ).format(count=len(title))
            )
        self.auth.videos().update(part="snippet", body={
            'id':video_id,
            'snippet': {
                'title': title,
                # The category ID has to be passed when we update the snippet, as per
                # https://developers.google.com/youtube/v3/docs/videos/update#request-body
                'categoryId': self.YOUTUBE_CATEGORY_ID
            }
        }).execute()
        return {}

    def publish_video(self, video_id):
        # A video is automatically published on youtube so we don't do anything here.
        # We could use this method to make videos public, but that would allow
        # course staff to make public any video.
        # TODO Actually, we should probably remove the "publish" button on the dashboard.
        return {}

    def create_video(self, payload, title=None):
        # We don't need to do anything here, because we handle the upload
        # ourselves. Also, the video was added to the playlist right after the
        # upload. Note that the upload call should return a dictionary
        # containing an ID, otherwise the following will not work.
        return self.get_video(payload["id"])

    def unpublish_video(self, video_id):
        return {}

    def set_thumbnail(self, video_id, url):
        # We do not support that for youtube.
        raise NotImplementedError()

    def iter_subtitles(self, video_id):
        for subtitle in self.auth.captions().list(part="id,snippet", videoId=video_id).execute()["items"]:
            yield self.convert_subtitle_to_dict(subtitle)

    def delete_video_subtitle(self, video_id, subtitle_id):
        self.auth.captions().delete(id=subtitle_id).execute()

    def upload_subtitle(self, video_id, file_object, language):
        name = self.find_next_subtitle_name(video_id, language)
        subtitle = self.auth.captions().insert(
            part="id,snippet", body={
                'snippet': {
                    'videoId': video_id,
                    'language': language,
                    'name': name,
                }
            },
            media_body=media_body(file_object)
        ).execute()
        return self.convert_subtitle_to_dict(subtitle)

    def find_next_subtitle_name(self, video_id, language):
        """
        Two subtitles with the same language may not have the same name. So
        when adding a new subtitle to a video, we need to check the names of
        other subtitles.
        """
        # Check existing subtitles
        existing_names = []
        existing_count = 0
        for subtitle in self.auth.captions().list(part="id,snippet", videoId=video_id).execute()["items"]:
            if subtitle['snippet']['language'] == language:
                existing_names.append(subtitle['snippet']['name'])
                existing_count += 1
        if existing_count == 0:
            return ""

        # Find new name for the subtitle
        subtitle_id = existing_count - 1
        subtitle_name = None
        while subtitle_name is None or subtitle_name in existing_names:
            subtitle_id += 1
            subtitle_name = "#{}".format(subtitle_id)
        return subtitle_name

    def download_subtitle(self, subtitle_id):
        """
        Return the content of the subtitle file, stored on youtube.
        """
        return self.auth.captions().download(id=subtitle_id).execute()

    def get_upload_url(self):
        # Note: because the user cannot upload directly to youtube from its
        # browser, it needs to upload to the CMS first. Thus, the reverse()
        # call used here will work only in the CMS.
        url = reverse(
            "youtube:upload_video", kwargs={
                "course_key_string": self.course_key_string
            }
        )
        return {
            "url": url,
            "file_parameter_name": self.FILE_PARAMETER_NAME
        }

    def upload_video(self, file_object):
        # TODO: error management: what if video upload fails?
        # 1) Upload video
        video = self.auth.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": file_object.name[:100],
                    "categoryId": self.YOUTUBE_CATEGORY_ID
                },
                "status": {
                    "privacyStatus": "unlisted"
                }
            },
            media_body=media_body(file_object)
        ).execute()

        # 2) Add to playlist (and just pray that the request does not abort
        # before the video is added to the playlist)
        video_id = video["id"]
        self.auth.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": self.playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id,
                    }
                }
            }
        ).execute()

        # This object will be passed to the create_video handler
        return {
            "id": video_id
        }


def iter_page_items(func, *args, **kwargs):
    """
    Iterate on the results of every page.
    Args:
        func: function to be called with args, kwargs as arguments. The
        pageToken argument will be added. Then the 'execute' method will be
        called on the result of each call.
    """
    page_token = None
    while True:
        kwargs["pageToken"] = page_token
        results = func(*args, **kwargs).execute()
        for item in results["items"]:
            yield item
        page_token = results.get("nextPageToken")
        if page_token is None:
            break

def media_body(file_object):
    # Guess mimetype
    mimetype, _ = mimetypes.guess_type(file_object.name)
    if mimetype is None:
        # Guess failed, use octet-stream.
        mimetype = 'application/octet-stream'
    return MediaIoBaseUpload(file_object, mimetype=mimetype)


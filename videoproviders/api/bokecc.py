import json
import logging
import time
import urllib

from django.conf import settings

from .base import BaseClient, ClientError, MissingVideo
from ..models import BokeCCCourseSettings

logger = logging.getLogger(__name__)


class Client(BaseClient):
    """
    This is the client for the Bokecc video provider.
    There is only one account per platform's instance. Video are stored under
    different categories representing each university
    """

    def __init__(self, course_key_string):
        super(Client, self).__init__(course_key_string)
        self.course_key_string = course_key_string
        self._playlist_id = None

    @property
    def playlist_id(self):
        # The concept of 'playlist' will be used to split videos from different courses
        # However there are limitations due to the fact that playlists are limited to 100 elements
        if self._playlist_id is None:
            # Build the playlist if from the course_key_string and check if any
            # Bokecc playlist exists with this name
            self._playlist_id = BokeccUtil.get_or_create_playlist(self.course_id)
        return self._playlist_id

    ####################
    # Overridden methods
    ####################

    def get_auth(self):
        # Here there is no specific Auth credentials except the ones provided in the general
        # Settings (see BOKECC_APIKEY and BOKECC_USERID)
        api_salt_key, user_id = BokeccUtil.get_auth()
        return {"user_id": user_id, "salt_key": api_salt_key}

    def get_video(self, video_id, player_width="890px", player_height="375px"):
        """Return a single video, identified by its id."""
        video = {}
        # Get video info - playcode :
        # {
        #     "video": {
        #         "playcode":"<script src='xxx' ...</script>"
        #     }
        # }
        bokecc_video_playcode = BokeccUtil.bokecc_request_get(
            'video/playcode',
            params={'videoid': video_id,
                    'playerid': BokeccUtil.BOKECC_PLAYER_ID,
                    'auto_play': 'false',
                    'player_width': player_width,
                    'player_height': player_height}
        )
        # Get video info - Format :
        # {
        #     "video": {
        #         "id": "XXX",
        #         "title": "TITLKE",
        #         "desp": "DESC",
        #         "tags": " ",
        #         "duration": 10,
        #         "category": "YYY",
        #         "image": "http://img.bokecc.com/comimage/XXXXX",
        #         "imageindex": 0,
        #         "image-alternate": [
        #             {
        #                 "index": 0,
        #                 "url": "ZZZZ"
        #             },
        #         ]
        #     }
        # }
        bokecc_video_infos = BokeccUtil.bokecc_request_get(
            'video',
            params={'videoid': video_id, }
        )
        js_script_url = ''
        if "video" in bokecc_video_playcode and "video" in bokecc_video_infos:
            # extract javascript URL so it in in HTTPS
            import re
            real_url_match = re.search('src="http://([^"]+)" ',
                                       bokecc_video_playcode["video"]["playcode"])
            if real_url_match:
                js_script_url = "https://" + real_url_match.group(1)
            video['js_script_url'] = js_script_url
            video['id'] = video_id
            video['title'] = bokecc_video_infos['video']["title"]
            video['prev_image'] = bokecc_video_infos['video']["image"]
            video['thumbnail_url'] = bokecc_video_infos['video']["image"]
            video['created_at'] = ''
            video['status'] = "ready"
            return video

        raise MissingVideo()

    def iter_videos(self):
        """
        Iterates through the videos
        :return: a list of videos  
        """

        playlist_id = BokeccUtil.get_or_create_playlist(self.course_id)
        # Return all videos in playlist
        if playlist_id is not None:
            response = BokeccUtil.bokecc_request_get(
                'playlist/update',
                params={'playlistid': playlist_id, }
            )
            if "playlist" in response:
                video_id_list = response["playlist"]["video"]
                for video in video_id_list:
                    # Get full info for this video
                    video_id = video["id"]
                    if video_id != BokeccUtil.BOKECC_PLAYLIST_FAKE_VIDEO_ID_HACK:
                        yield self.get_video(video_id)

    def delete_video(self, video_id):
        """Delete a video

               Returns:
                   None
        """
        response = BokeccUtil.bokecc_request_get(
            'video/delete',
            params={'videoid': video_id, }
        )
        if "error" in response:
            raise ClientError("Impossible to delete video")

    def update_video_title(self, video_id, title):
        """Change a video title"""
        response = BokeccUtil.bokecc_request_get(
            'video/update',
            params={
                'videoid': video_id,
                'title': title.encode('utf-8'),
            }
        )
        if "error" in response:
            raise ClientError("Impossible to change name for video")
        else:
            # As per youtube implementation the return value is not used
            return {}

    ###############################################
    # To implement later depending on actual needs
    ###############################################

    def iter_subtitles(self, video_id):
        pass

    def get_subtitles(self, video_id):
        # We do not yet manage subtitles
        pass

    def upload_subtitle(self, video_id, file_object, language):
        pass

    def delete_video_subtitle(self, video_id, subtitle_id):
        pass

    def upload_thumbnail(self, video_id, file_object):
        pass

    def get_upload_url(self, origin=None):
        """Get a URL for uploading a video.
            Args:
                origin (str): current domain name that may be included in CORS headers

            Returns: {
                "url": "http...", # url on which a POST should be made
                "file_parameter_name": "path" # name of the file parameter to be sent to the url
            }
        """
        pass

    def create_video(self, payload, title=None):
        response = BokeccUtil.bokecc_request_get(
            'video/create',
            params={'title': title.encode('utf-8'),
                    'tag': '',
                    'description': title.encode('utf-8'),
                    'categoryid': ''
                    }
        )
        if "error" in response:
            raise ClientError("Error creating videos")
        return response


class BokeccUtil:
    BOKECC_PLAYER_ID = getattr(settings, 'BOKECC_PLAYER_ID', '30130B6BCFC187A4')
    BOKECC_URL = getattr(settings, 'BOKECC_URL', 'http://spark.bokecc.com/api/')

    # This is a complete hack: we need to have a video id to create a playlist
    # So this is an id of a small video that will always be part of any playlist
    # Warning: if this video is deleted we will not be able to create a playlist
    BOKECC_PLAYLIST_FAKE_VIDEO_ID_HACK = getattr(settings, 'BOKECC_FAKE_VIDEO_ID', '448AA25E88D95C639C33DC5901307461')

    @staticmethod
    def get_or_create_playlist( course_id):
        playlist_id = None
        try:
            # Read from BokeCCSettings object
            course_settings = BokeCCCourseSettings.objects.get(course_id=course_id)
            playlist_id = course_settings.playlist_id
        except BokeCCCourseSettings.DoesNotExist:
            # Then look for it on the Bokecc end point
            response = BokeccUtil.bokecc_request_get(
                'playlists',
                params={}
            )

            if 'playlists' in response:
                for playlist in response['playlists']['playlist']:
                    if playlist["name"] == str(course_id):
                        playlist_id = playlist["id"]
                        break

            # We have not found the playlist on the remote server, so we need to create it
            if playlist_id is None:
                # create the given playlist
                response = BokeccUtil.bokecc_request_get(
                    'playlist/create',
                    params={'name': str(course_id),
                            'videoid': BokeccUtil.BOKECC_PLAYLIST_FAKE_VIDEO_ID_HACK,
                            }
                )
                if "playlist" in response:
                    playlist_id = response["playlist"]["id"]
            if playlist_id is not None:
                course_settings, _created = BokeCCCourseSettings.objects.get_or_create(course_id=course_id)
                course_settings.playlist_id = playlist_id
                course_settings.save()
            else:
                raise ClientError("Impossible to create playlist for course")
        return playlist_id

    ####################
    # Utilities
    ####################
    @staticmethod
    def bokecc_request_get(endpoint, params=None):

        if params is None:
            params = []

        api_key_salt,bokecc_user_id = BokeccUtil.get_auth()
        full_req_params = params
        full_req_params['userid'] = bokecc_user_id
        full_req_params['format'] = 'json'

        url = BokeccUtil.BOKECC_URL + endpoint + '?'
        complete_url = url + BokeccUtil.__bokecc_get_hqs(full_req_params, api_key_salt)
        f = urllib.urlopen(complete_url)
        response = json.loads(f.read())

        if "error" in response:
            logger.error("Bokecc error: %s", response['error'])
        return response

    @staticmethod
    def __bokecc_get_hqs(q, api_key_salt):
        import hashlib
        qftime = 'time=%d' % int(time.time())
        salt = 'salt=%s' % api_key_salt
        qftail = '&%s&%s' % (qftime, salt)
        # Build URL and encode parameters
        l = []
        for k in q:
            k = urllib.quote_plus(str(k))
            v = urllib.quote_plus(str(q[k]))
            url_param = '%s=%s' % (k, v)
            l.append(url_param)
        l.sort()
        # Build and concatenate URL
        qs = '&'.join(l)
        qf = qs + qftail
        hashqf = 'hash=%s' % (hashlib.new('md5', qf).hexdigest().upper())
        hqs = '&'.join((qs, qftime, hashqf))
        return hqs

    @staticmethod
    def get_auth():
        api_salt_key = getattr(settings, 'BOKECC_APIKEY', '')
        user_id = getattr(settings, 'BOKECC_USERID', '')
        return api_salt_key, user_id



from django.conf import settings

from .base import BaseClient, ClientError, MissingVideo, MissingCredentials
from ..models import BokeCCCourseSettings

import logging

logger = logging.getLogger(__name__)

class Client(BaseClient):
    """
    This is the client for the Bokecc video provider. 
    There is only one account per platform's instance. Video are stored under
    different categories representing each university

    """

    BOKECC_PLAYER_ID = getattr(settings, 'BOKECC_PLAYER_ID', '30130B6BCFC187A4')
    BOKECC_URL = getattr(settings, 'BOKECC_URL', 'http://spark.bokecc.com/api/')


    # This is a complete hack: we need to have a video id to create a playlist
    # So this is an id of a small video that will always be part of any playlist
    # Reminder: if this video is
    BOKECC_PLAYLIST_FAKE_VIDEO_ID_HACK ='448AA25E88D95C639C33DC5901307461'

    def __init__(self, course_key_string):
        super(Client, self).__init__(course_key_string)
        self.course_key_string = course_key_string
        self._playlist_id = None

    @property
    def playlist_id(self):
        # The concept of 'playlist' will be used to split videos from different courses
        # However there are limitations due to the fact that playlists are limited to 100 elements
        if self._playlist_id is None :
          # Build the playlist if from the course_key_string and check if any
          # Bokecc playlist exists with this name
          self._playlist_id = self._get_or_create_playlist()
        return self._playlist_id

    ####################
    # Overridden methods
    ####################

    def get_auth(self):
        # Here there is no specific Auth credentials except the ones provided in the general
        # Settings (see BOKECC_APIKEY and BOKECC_USERID)
        API_SALT_KEY = getattr(settings, 'BOKECC_APIKEY', '')
        USER_ID = getattr(settings, 'BOKECC_USERID', '')
        return {"user_id":USER_ID,"salt_key":API_SALT_KEY }

    def get_video(self, video_id):
        video = {}
        bokecc_video_infos = self.__bkcc_request_get(
            self.BOKECC_URL,
            'video/playcode',
            log_error=True,
            params = {'videoid': video_id,
                      'playerid': self.BOKECC_PLAYER_ID,
                      'auto_play': 'false',
                      'player_width': "890px",
                      'player_height': "375px",
                      }
        )
        js_script_url = ''
        if "video" in bokecc_video_infos :
            # extract javascript URL so it in in HTTPS
            import re
            real_url_match = re.search('src="http://([^"]+)" ',bokecc_video_infos["video"]["playcode"])
            if real_url_match:
                js_script_url  =  "https://" +  real_url_match.group(1)
            video['js_script_url'] = js_script_url
            video['id'] = video_id
            return video

        raise MissingVideo()

    def iter_videos(self):
        playlist_id = self._get_or_create_playlist()
        # Return all videos in playlist
        video_list = []
        if playlist_id is not None:
            response = self.__bkcc_request_get(
                self.BOKECC_URL,
                'playlist/update',
                log_error=True,
                params={'playlistid': playlist_id,}
            )
            if "playlist" in response:
                video_id_list = response["playlist"]["video"]
                for video in video_id_list:
                    # Get full info for this video
                    response = self.__bkcc_request_get(
                        self.BOKECC_URL,
                        'video',
                        log_error=True,
                        params={'videoid': video["id"],}
                    )
                    if "video" in response:
                        video_list.append(response["video"])
        else:
            response = self.__bkcc_request_get(
                self.BOKECC_URL,
                'video',
                log_error=True,
                params={}
            )
            if "videos" in response:
                video_list = response["videos"]["video"]

        # Format :
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

        for video in video_list:
                    yield video


    def get_subtitles(self, video_id):
        # We do not yet manage subtitles
        pass

    def create_video(self, payload, title=None):
        response = self.__bkcc_request_get(
            self.BOKECC_URL,
            'video/create',
            log_error=True,
            params={'title': title.encode('utf-8'),
                    'tag': '',
                    'description': title.encode('utf-8'),
                    'categoryid':''
                    }
        )
        return response


    ####################
    # Utilities
    ####################

    def __bkcc_request_get(self, bokecc_base_url, endpoint, log_error=False, params=[]):
        import time
        import urllib
        import hashlib
        import json
        auth = self.get_auth()
        api_key_salt = auth["salt_key"]
        bokecc_user_id = auth["user_id"]

        # This is a slightly modified part of the Spark API demo
        # TODO: improve the way the URL is built
        class thqs(object):
            def my_urlencode(self, q):
                l = []
                for k in q:
                    k = urllib.quote_plus(str(k))
                    v = urllib.quote_plus(str(q[k]))
                    url_param = '%s=%s' % (k, v)
                    l.append(url_param)
                l.sort()
                return '&'.join(l)

            def get_hqs(self, q, api_key_salt):
                qftime = 'time=%d' % int(time.time())
                salt = 'salt=%s' % api_key_salt
                qftail = '&%s&%s' % (qftime, salt)

                qs = self.my_urlencode(q)
                qf = qs + qftail
                hashqf = 'hash=%s' % (hashlib.new('md5', qf).hexdigest().upper())
                hqs = '&'.join((qs, qftime, hashqf))
                return hqs

        current_time = '%d' % int(time.time())
        full_req_params = params
        full_req_params['userid'] = bokecc_user_id
        full_req_params['format'] = 'json'

        url = bokecc_base_url + endpoint + '?'
        complete_url = url + thqs().get_hqs(full_req_params, api_key_salt)
        f = urllib.urlopen(complete_url)
        response = json.loads(f.read())

        if "error" in response:
            logger.error("Bokecc error: %s", response['error'])
        return response

    def _get_or_create_playlist(self):
        playlist_id = None
        try:
            # Read from BokeCCSettings object
            course_settings = BokeCCCourseSettings.objects.get(course_id=self.course_id)
            playlist_id = course_settings.playlist_id
        except BokeCCCourseSettings.DoesNotExist:
           # Then look for it on the Bokecc end point
           response = self.__bkcc_request_get(
                self.BOKECC_URL,
                'playlists',
                log_error=True,
                params={}
            )

           if 'playlists' in response:
                for playlist in response['playlists']['playlist']:
                    if playlist["name"] == self.course_key_string:
                        playlist_id = playlist["id"]
                        break

           # We have not found the playlist on the remote server, so we need to create it
           if playlist_id is None:
            # create the given playlist
            response = self.__bkcc_request_get(
                self.BOKECC_URL,
                'playlist/create',
                log_error=True,
                params={'name': self.course_key_string,
                        'videoid': self.BOKECC_PLAYLIST_FAKE_VIDEO_ID_HACK,
                        }
                )
            if "playlist" in response:
                playlist_id = response["playlist"]["id"]
           if playlist_id is not None:
            course_settings, _created = BokeCCCourseSettings.objects.get_or_create(course_id=self.course_id)
            course_settings.playlist_id = playlist_id
            course_settings.save()
           else:
                raise ClientError("Impossible to create playlist for course")
        return playlist_id
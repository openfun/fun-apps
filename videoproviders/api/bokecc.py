
from django.conf import settings

from .base import BaseClient, ClientError, MissingVideo, MissingCredentials


class Client(BaseClient):
    """
    This is the client for the Bokecc video provider. 
    There is only one account per platform's instance. Video are stored under
    different categories representing each university

    """

    BOKECC_PLAYER_ID = getattr(settings, 'BOKECC_PLAYER_ID', '30130B6BCFC187A4')
    BOKECC_URL = getattr(settings, 'BOKECC_URL', 'http://spark.bokecc.com/api/')
    API_SALT_KEY = getattr(settings, 'BOKECC_APIKEY', '')
    USER_ID =  getattr(settings, 'BOKECC_USERID', '')


    def __init__(self, course_key_string):
        super(Client, self).__init__(course_key_string)
        self.course_key_string = course_key_string


    ####################
    # Overridden methods
    ####################

    # This part will need to be moved into fun-apps as a specific BokeCC videoclient
    def __bkcc_request_get(self, bokecc_base_url, endpoint, api_key_salt, user_id,  log_error=False, params = []):
        import time
        import urllib
        import hashlib
        import json

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
        full_req_params['userid'] = user_id
        full_req_params['format'] = 'json'

        url = bokecc_base_url + endpoint +'?'
        complete_url = url+ thqs().get_hqs(full_req_params,api_key_salt)
        f = urllib.urlopen(complete_url)
        response =  json.loads(f.read())

        if "error" in response:
            logger.error("Bokecc error: %s", response['error'])
        return response


    def get_video(self, video_id):
        video = {}
        bokecc_video_infos = self.__bkcc_request_get(
            self.BOKECC_URL,
            'video/playcode',
            self.API_SALT_KEY,
            self.USER_ID,
            log_error=True,
            params = {'videoid': video_id,
                      'playerid': self.BOKECC_PLAYER_ID,
                      'auto_play': 'false',
                      'playerwidth': "890px",
                      'playerheight': "375px",
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

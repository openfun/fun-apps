# -*- coding: utf-8 -*-
import lxml.etree
import logging
import os
import requests
import requests.auth

from django.core.cache import get_cache
from django.utils.translation import gettext as _

from fun.utils.i18n import language_name
from .base import BaseClient, ClientError, MissingCredentials
from .. import models

logger = logging.getLogger(__name__)


class LibcastUrls(object):
    # Note that these settings will probably have to be different in microsites
    MEDIA_NAME = 'fun-libcast-com'
    API_URL_PATTERN = 'https://console.libcast.com/services/{}'
    FUN_LIBCAST_URL_PATTERN = 'https://fun.libcast.com/{}'

    def __init__(self, course_key_string):
        """
        Args:
            course_key_string (str)
        """
        self.course_key_string = course_key_string

    def libcast_url(self, endpoint):
        return self.url(self.API_URL_PATTERN, endpoint)
    def fun_libcast_url(self, endpoint):
        # For some reason, this root url is used only for flavor urls.
        return self.url(self.FUN_LIBCAST_URL_PATTERN, endpoint)

    def url(self, pattern, endpoint):
        path = endpoint.strip("/")
        return pattern.format(path)

    @property
    def slug(self):
        return slugify(self.course_key_string)

    def streams_path(self):
        return "media/{}/streams".format(self.MEDIA_NAME)

    def stream_resources_path(self):
        return 'stream/{}/resources'.format(self.slug)

    def file_path(self, file_slug):
        return 'file/{}'.format(file_slug)

    def directory_url(self):
        return self.libcast_url(self.directory_path())

    def directory_path(self):
        return 'files/{}'.format(slugify(self.course_key_string))

    def resource_path(self, slug):
        return 'resource/{}'.format(slug)

    def upload_links_path(self):
        return "files/{}/upload_links".format(self.slug)

    def subtitle_href(self, video_id, subtitle_id):
        # Note that the download url for subtitles is not a file path, but a resource path.
        return self.libcast_url(self.resource_path(video_id) + "/subtitles/{}".format(subtitle_id))

    def subtitle_path(self, video_id, subtitle_id):
        return "file/{}/subtitles/{}".format(video_id, subtitle_id)

    def subtitles_path(self, video_id):
        return "file/{}/subtitles".format(video_id)

    def flavor_url(self, video_id, label):
        path = self.resource_path(video_id) + "/flavor/video/fun-{}.mp4".format(slugify(label))
        return self.fun_libcast_url(path)


class LibcastAccountVerifierMixin(object):
    """
    We need to make sure that the Libcast account is properly configured at
    runtime; so we store a cache key with an expiry date, and the account is
    verified when the key expires.
    """

    # The libcast account will be verified with this periodicity
    LIBCAST_CONFIG_CHECK_PERIOD_SECONDS = 24*60*60
    CACHE_NAME = 'libcast'

    def ensure_course_is_configured(self):
        """
        Make sure that everything is ready in the Libcast account for upload.

        This will run on every CMS instance every LIBCAST_CONFIG_CHECK_PERIOD_SECONDS.
        """
        cache = get_cache(self.CACHE_NAME)
        if not cache.get(self.course_key_string):
            self.ensure_course_directory_exists()
            parent_stream_slug = self.get_or_create_parent_stream()
            self.ensure_stream_exists(self.course_key_string, parent_stream_slug)
            cache.set(self.course_key_string, self.LIBCAST_CONFIG_CHECK_PERIOD_SECONDS)

    def ensure_course_directory_exists(self):
        """Check for the existence of a folder (possibly in a subdirectory) and create it if necessary.

        Raise a ClientError if the directory could not be created. The obtained
        folder will be checked to verify we have the correct href. If not, it
        probably means the course name contains some special, unexpected
        characters.
        """
        response = self.get("files/{}".format(self.directory_slug))
        if response.status_code >= 400:
            # Create all subdirectories starting from the bottom.
            # If any directory cannot be created, this will raise a ClientError.
            response = self.post("files", params={"name": self.course_key_string})
            if response.status_code >= 400:
                raise ClientError(_("Could not create folder {}").format(self.course_key_string))
            # Check obtained href is what we expect
            etree = parse_xml(response)
            folder_href = etree.attrib['href']
            expected_href = self.urls.directory_url()
            if folder_href != expected_href:
                logger.error("Libcast folder slug is not the one expected. Bad"
                             "things will follow! Expected %s, got %s for course %s",
                             expected_href, folder_href, self.course_key_string)

    def get_or_create_parent_stream(self):
        """Get or create the parent stream of the course stream.

        Returns:
            stream_slug (str): slug of the parent stream
        """
        response = self.get(self.urls.streams_path())
        if response.status_code >= 400:
            raise ClientError(_("Could not load organisation streams"))
        etree = parse_xml(response)
        for stream in etree.iter('stream'):
            if stream.find('title').text == self.org:
                return stream.find('slug').text
        # Create stream
        stream = self.create_stream(self.org, self.VISIBILITY_VISIBLE)
        return stream.find('slug').text

    def ensure_stream_exists(self, title, parent_stream=None):
        """
        Make sure the stream with the given title exists.

        If the stream does not exist, it will be created as a child of the given parent.

        Args:
            title (str): stream title
            parent_stream (str): parent stream slug.
        """
        stream_slug = slugify(title)
        response = self.get("stream/{}".format(stream_slug))
        if response.status_code >= 400:
            return self.create_stream(title, self.VISIBILITY_HIDDEN, parent_stream)

    def create_stream(self, title, visibility, parent_stream=None):
        params = {
            "title": title,
            "visibility": visibility
        }
        if parent_stream:
            params["parent_stream"] = parent_stream
        response = self.post(self.urls.streams_path(), params=params)
        if response.status_code >= 400:
            raise ClientError(_("Could not create stream {}").format(title))
        return parse_xml(response)


class Client(BaseClient, LibcastAccountVerifierMixin):
    """Client for the Libcast API

    The API is documented here: https://developers.libcast.com/api/03-api/

    The credentials used for interacting with the API are stored in the database.
    The videos for each course are stored in a directory with the slug
    'org-course-run'. Each video that was uploaded to this directory is sent to
    a playlist (i.e: a stream) with the same slug. This playlist is a
    sub-playlist of the 'org' playlist.
    """

    VISIBILITY_HIDDEN = 'hidden'
    VISIBILITY_VISIBLE = 'visible'

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.urls = LibcastUrls(self.course_key_string)
        if self.course_key_string:
            self.ensure_course_is_configured()

    @property
    def directory_slug(self):
        """Directory that stores the video files"""
        return slugify(self.course_key_string)

    @property
    def course_key_string(self):
        return unicode(self.course_id)

    def get_resource_file(self, resource):
        file_slug = self.get_resource_file_slug(resource)
        response = self.get(self.urls.file_path(file_slug))
        if response.status_code >= 400:
            raise ClientError(_("Could not fetch file"))
        return parse_xml(response)

    def get_resource_file_slug(self, resource):
        file_href = resource.find("file").attrib['href']
        return os.path.basename(file_href)

    def get_resource(self, slug):
        response = self.get(self.urls.resource_path(slug))
        if response.status_code >= 400:
            raise ClientError(_("Could not fetch video"))
        return parse_xml(response)

    def request(self, endpoint, method='GET', params=None, files=None):
        return http_request(
            self.urls.libcast_url(endpoint), method=method, params=params,
            files=files, auth=self.auth
        )

    def convert_resource_to_video(self, resource, file_obj):
        visibility = resource.find('visibility').text
        # TODO we could take into account the "encoding_progress" integer value of the file object
        encoding_status = file_obj.find('encoding_status').text
        if encoding_status != 'finished':
            status = 'processing'
        elif visibility == 'visible':
            status = 'published'
        else:
            status = 'ready'
        slug = resource.find('slug').text
        if status == "processing":
            video_sources = []
            external_link = ""
        else:
            video_sources = self.video_sources(slug)
            external_link = self.urls.flavor_url(slug, 'SD')

        published_at = resource.find('published_at').text
        created_at = self.timestamp_to_str(int(published_at)) if published_at else None
        return {
            'id': slug,
            'created_at': created_at,
            'title':  resource.find('title').text,
            'subtitles': self.get_resource_subtitles(resource),
            'status': status,
            'thumbnail_url': self.get_resource_thumbnail_url(resource),
            'video_sources': video_sources,
            'external_link': external_link
        }

    def video_sources(self, video_id):
        def video_source(label, res):
            return {
                "label": label,
                "res": res,
                "type": "video/mp4",
                "url": self.urls.flavor_url(video_id, label.lower())
            }
        return [
            video_source("HD", "720"),
            video_source("SD", "512"),
            video_source("LD", "320"),
        ]

    def downloadable_files(self, video_id):
        def downloadable_file(url, name):
            return {
                "url": url,
                "name": name,
            }
        return [
            downloadable_file(self.urls.flavor_url(video_id, 'hd'), _("High Definition (720p)")),
            downloadable_file(self.urls.flavor_url(video_id, 'sd'), _("Standard (512p)")),
            downloadable_file(self.urls.flavor_url(video_id, 'ld'), _("Smartphone (320p)")),
        ]


    def create_resource(self, file_slug, title):
        response = self.post(self.urls.stream_resources_path(), {
            "title": title,
            "file": file_slug,
            "visibility": self.VISIBILITY_HIDDEN,
        })
        if response.status_code >= 400:
            raise ClientError(_("Could not create resource"))
        return parse_xml(response)

    def convert_subtitle_to_dict(self, subtitle):
        subtitle_href = subtitle.attrib['href']
        # Subtitles have no id, so we refer to them via their file name
        subtitle_id = os.path.basename(subtitle_href)
        return {
            'id': subtitle_id,
            'language': subtitle.attrib['language'],
            'language_label': language_name(subtitle.attrib['language']),
            'url': subtitle_href,
        }

    ####################
    # Overridden methods
    ####################

    def get_auth(self):
        """Libcast API uses HTTP Digest authentication"""
        try:
            libcast_auth = models.LibcastAuth.objects.get_for_course(self.course_module)
        except models.LibcastAuth.DoesNotExist:
            raise MissingCredentials(self.org)
        if not all([libcast_auth.username, libcast_auth.api_key]):
            raise MissingCredentials(self.org)
        # We don't store the nonce here, which means that each session
        # will take a while to start. We could optimise this by storing the
        # nonce in a cache, but the nonce storage would be quite complex.
        return requests.auth.HTTPDigestAuth(libcast_auth.username, libcast_auth.api_key)

    def iter_videos(self):
        """
        If videos were not created, they are created on-the-fly. This is the
        only way we have found to keep the video folder and the playlist in
        sync.
        """
        # Iterate on course playlist
        etree = parse_xml(self.get(self.urls.stream_resources_path()))
        resources = {
            resource.find('file').attrib['href']: resource for resource in etree.iter('resource')
        }

        # Iterate on folder and create associated resources if necessary
        etree = parse_xml(self.get(self.urls.directory_path()))
        for file_obj in etree.iter('file'):
            file_href = file_obj.attrib['href']
            file_slug = file_obj.find('slug').text
            file_name = file_obj.find('name').text
            resource = resources.get(file_href)
            if not resource:
                resource = self.create_resource(file_slug, file_name)
            yield self.convert_resource_to_video(resource, file_obj)

    def get_video(self, video_id):
        resource = self.get_resource(video_id)
        file_obj = self.get_resource_file(resource)
        return self.convert_resource_to_video(resource, file_obj)

    def delete_video(self, video_id):
        # Deleting the file causes the deletion of associated resources
        # Note that if multiple resources are associated to a single file, all
        # resources will be deleted.
        resource = self.get_resource(video_id)
        file_slug = self.get_resource_file_slug(resource)
        response = self.delete(self.urls.file_path(file_slug))
        if response.status_code >= 400:
            raise ClientError(_("Could not delete video"))

    def update_video_title(self, video_id, title):
        response = self.put(self.urls.resource_path(video_id), {"title": title})
        if response.status_code >= 400:
            raise ClientError(_("Could not change video title"))
        return {}

    def get_upload_url(self):
        response = self.post(self.urls.upload_links_path())
        if response.status_code >= 400:
            raise ClientError(_("Could not fetch upload url"))
        etree = parse_xml(response)
        return {
            "url": etree.find("link[@rel='json']").attrib["href"],
            "file_parameter_name": "file[path]"
        }

    def create_video(self, payload, title=None):
        """Add the video to the stream after it has been uploaded"""
        file_slug = payload.get('result', {}).get('slug')
        if not file_slug:
            raise ClientError(_("Undefined file slug"))
        resource = self.create_resource(file_slug, title)
        file_obj = self.get_resource_file(resource)
        return self.convert_resource_to_video(resource, file_obj)

    def publish_video(self, video_id):
        return self.set_video_visibility(video_id, self.VISIBILITY_VISIBLE)

    def unpublish_video(self, video_id):
        return self.set_video_visibility(video_id, self.VISIBILITY_HIDDEN)

    def set_video_visibility(self, video_id, visibility):
        response = self.put(self.urls.resource_path(video_id), {'visibility': visibility})
        if response.status_code >= 400:
            raise ClientError(_("Could not change video visibility"))
        return {}

    def get_video_subtitles(self, video_id):
        resource = self.get_resource(video_id)
        return self.get_resource_subtitles(resource)

    def get_resource_thumbnail_url(self, resource):
        return resource.find('thumbnail').text

    def get_resource_subtitles(self, resource):
        """Get the subtitles associated to a resource

        Args:
            resource (etree)
        """
        subtitles = resource.find('subtitles')
        if not subtitles:
            return []
        return [
            self.convert_subtitle_to_dict(subtitle)
            for subtitle in subtitles.iter('subtitle')
        ]

    def upload_subtitle(self, video_id, file_object, language):
        response = self.post(self.urls.subtitles_path(video_id),
                             files={'subtitle': file_object},
                             params={'language': language})
        if response.status_code >= 400:
            raise ClientError(_("Could not upload subtitle"))

    def delete_video_subtitle(self, video_id, subtitle_id):
        response = self.delete(self.urls.subtitle_path(video_id, subtitle_id))
        if response.status_code >= 400:
            raise ClientError(_("Could not delete subtitle"))

    def set_thumbnail(self, video_id, url):
        # TODO
        pass


def parse_xml(response):
    """
    Parse xml code; raise ClientError on failure.

    Args:
        response (requests.models.Response)

    Returns:
        etree (lxml.etree)
    """
    try:
        return lxml.etree.fromstring(response.content)
    except:
        logger.error("Could not parse libcast response: %s",
                     response.content.decode('utf-8'))
        raise ClientError(_("Could not parse response"))

def slugify(string):
    """Convert an object name to a libcast slug

    Returns:
        slug (str)
    """
    return string.lower().replace('/', '-')

def http_request(url, method='GET', params=None, files=None, auth=None):
    func = getattr(requests, method.lower())
    kwargs = {
        'auth': auth,
    }
    if method.upper() == 'GET':
        kwargs['params'] = params
    else:
        kwargs['data'] = params
        kwargs['files'] = files
    response = func(url, **kwargs)
    if response.status_code >= 400:
        logger.error(u"Libcast client error url=%s, method=%s, params=%s, response:\n%s",
                     url, method, params, response.content.decode('utf-8'))
    return response


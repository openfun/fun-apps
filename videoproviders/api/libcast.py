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
    API_URL_PATTERN = 'https://api.libcast.com/{}'
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

    def streams_path(self):
        return "media/{}/streams".format(self.MEDIA_NAME)

    def stream_resources_path(self, slug):
        return 'stream/{}/resources'.format(slug)

    def file_path(self, file_slug):
        return 'file/{}'.format(file_slug)

    def directory_url(self, directory_slug):
        return self.libcast_url(self.directory_path(directory_slug))

    def root_directory_path(self):
        return "files"

    def directory_path(self, directory_slug):
        return 'files/{}'.format(directory_slug)

    def resource_path(self, slug):
        return 'resource/{}'.format(slug)

    def upload_links_path(self, directory_slug):
        return "files/{}/upload_links".format(directory_slug)

    def subtitle_href(self, video_id, subtitle_id):
        # Note that the download url for subtitles is not a file path, but a resource path.
        return self.fun_libcast_url(self.resource_path(video_id) + "/subtitles/{}".format(subtitle_id))

    def subtitle_path(self, file_slug, subtitle_id):
        return "file/{}/subtitles/{}".format(file_slug, subtitle_id)

    def subtitles_path(self, file_slug):
        return "file/{}/subtitles".format(file_slug)

    def flavor_url(self, video_id, label):
        path = self.resource_path(video_id) + "/flavor/video/fun-{}.mp4".format(slugify(label))
        return self.fun_libcast_url(path)


class Client(BaseClient):
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
    DEFAULT_TIMEOUT_SECONDS = 10

    def __init__(self, course_key_string):
        super(Client, self).__init__(course_key_string)
        self.urls = LibcastUrls(self.course_key_string)
        self._settings = None

    @property
    def course_key_string(self):
        return unicode(self.course_id)

    @property
    def settings(self):
        """Libcast course settings

        Returns:
            _settings (LibcastCourseSettings): if the settings object does not
                exist, the course configuration will be checked and the settings
                object will be created afterwards.
        """
        if not self.course_key_string:
            return None
        if self._settings is None:
            try:
                settings = models.LibcastCourseSettings.objects.get(
                    course=self.course_key_string
                )
                if not settings.directory_slug or not settings.stream_slug:
                    raise models.LibcastCourseSettings.DoesNotExist()
            except models.LibcastCourseSettings.DoesNotExist:
                directory_slug, stream_slug = self.ensure_course_is_configured()
                # Try to retrieve object in order to avoid a race condition
                settings, _created = models.LibcastCourseSettings.objects.get_or_create(
                    course=self.course_key_string
                )
                settings.directory_slug = directory_slug
                settings.stream_slug = stream_slug
                settings.save()
            self._settings = settings
        return self._settings

    @property
    def stream_slug(self):
        """Stream that stores the course resources"""
        return self.settings.stream_slug

    @property
    def directory_slug(self):
        """Directory that stores the course video files"""
        return self.settings.directory_slug

    def get_resource_file(self, resource):
        file_slug = self.get_resource_file_slug(resource)
        return parse_xml(self.safe_get(
            self.urls.file_path(file_slug),
            message=_("Could not fetch file"))
        )

    def get_resource_file_slug(self, resource):
        file_href = resource.find("file").attrib['href']
        return os.path.basename(file_href)

    def get_resource(self, slug):
        return parse_xml(self.safe_get(
            self.urls.resource_path(slug),
            message=_("Could not fetch video")
        ))

    def convert_resource_to_video(self, resource, file_obj=None):
        """
        Args:
            resource (etree)
            file_obj (etree)
        """
        visibility = resource.find('visibility').text
        status = 'published' if visibility == 'visible' else 'ready'
        encoding_progress = None
        if file_obj is not None:
            encoding_status = file_obj.find('encoding_status').text
            if encoding_status != 'finished':
                status = 'processing'
                encoding_progress = file_obj.find('encoding_progress')
                if encoding_progress is not None:
                    encoding_progress = "%.2f" % float(encoding_progress.text)
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
            'encoding_progress': encoding_progress,
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
        return parse_xml(self.safe_post(
            self.urls.stream_resources_path(self.stream_slug), {
                "title": title,
                "file": file_slug,
                "visibility": self.VISIBILITY_HIDDEN,
            },
            message=_("Could not create resource")
        ))

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

    ##############################
    # Ensure account is configured
    # We need to make sure that the Libcast account is properly configured at
    # runtime. We check:
    # 1) The existence of the parent university stream
    # 2) The existence of the course stream
    # 3) The existence of the course folder
    ##############################

    def ensure_course_is_configured(self):
        """
        Make sure that everything is ready in the Libcast account for upload.
        This should be thread-safe, so we make use of a lock.

        Returns:
            directory_slug (str)
            stream_slug (str)
        """
        lock = "libcast-course-configuration: {}".format(self.course_key_string)
        lock_timeout_in_seconds = 20

        with SelfExpiringLock(lock, lock_timeout_in_seconds):
            directory_slug = self.ensure_course_directory_exists()
            parent_stream_slug = self.get_or_create_stream(self.org)
            stream_slug = self.get_or_create_stream(self.course_key_string, parent_stream=parent_stream_slug)
            return directory_slug, stream_slug

    def ensure_course_directory_exists(self):
        """Check for the existence of a folder and create it if necessary.

        Raise a ClientError if the directory could not be created.

        Returns:
            directory_slug (str)
        """
        files = parse_xml(self.safe_get(
            self.urls.root_directory_path(),
            message=_("Could not list course files")
        ))
        for directory in files.iter('directory'):
            directory_slug = os.path.basename(directory.attrib['href'])
            directory = parse_xml(self.safe_get(
                self.urls.directory_path(directory_slug),
                message=_("Could not list directory content {}").format(directory_slug)
            ))
            if directory.find('name').text == self.course_key_string:
                return directory_slug

        # Directory does not exist, let's create it
        directory = parse_xml(self.safe_post(
            self.urls.root_directory_path(),
            params={"name": self.course_key_string},
            message=_("Could not create folder {}").format(self.course_key_string)
        ))
        directory_slug = os.path.basename(directory.attrib['href'])
        return directory_slug

    def get_or_create_stream(self, title, parent_stream=None):
        """Find a stream and create it if it was not found.

        Note that the stream will be created as visible by default.

        Args:
            parent_stream (str): slug of the parent stream

        Returns:
            stream_slug (str)
        """
        streams = parse_xml(self.safe_get(
            self.urls.streams_path(), message=_("Could not load organisation streams")
        ))
        for stream in streams.iter('stream'):
            if stream.find('title').text == title:
                return stream.find('slug').text
        # Stream was not found, create it
        params = {
            "title": title,
            "visibility": self.VISIBILITY_VISIBLE
        }
        if parent_stream:
            params["parent_stream"] = parent_stream
        stream = parse_xml(self.safe_post(
            self.urls.streams_path(), params=params,
            message=_("Could not create stream {}").format(title)
        ))
        return stream.find('slug').text


    ####################
    # Overridden methods
    ####################

    def request(self, endpoint, method='GET', params=None, files=None):
        url = self.urls.libcast_url(endpoint)
        func = getattr(requests, method.lower())
        kwargs = {
            'auth': self.auth,
            'timeout': self.DEFAULT_TIMEOUT_SECONDS,
        }
        if method.upper() == 'GET':
            kwargs['params'] = params
        else:
            kwargs['data'] = params
            kwargs['files'] = files
        try:
            response = func(url, **kwargs)
        except requests.Timeout:
            raise ClientError(u"Libcast timeout url=%s, method=%s, params=%s" % (url, method, params))
        if response.status_code >= 400:
            logger.error(u"Libcast client error url=%s, method=%s, params=%s, status code=%d",
                         url, method, params, response.status_code)
        return response

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
        # Find course resources
        resources = parse_xml(self.safe_get(
            self.urls.stream_resources_path(self.stream_slug),
            params={
                "without-views": "true",
                "without-usages": "true",
            },
            message=_("Could not list videos")
        ))
        # file href -> resource dict
        resources = {
            resource.find('file').attrib['href']: resource for resource in resources.iter('resource')
        }

        # Iterate on folder and create associated resources if necessary
        files = parse_xml(self.safe_get(
            self.urls.directory_path(self.directory_slug),
            message=_("Could not list directory content {}".format(self.directory_slug))
        ))
        file_hrefs = set()
        for file_obj in files.iter('file'):
            file_href = file_obj.attrib['href']
            file_slug = file_obj.find('slug').text
            file_name = file_obj.find('name').text
            resource = resources.get(file_href)
            file_hrefs.add(file_href)
            if not resource:
                resource = self.create_resource(file_slug, file_name)
            yield self.convert_resource_to_video(resource, file_obj)

        # Iterate on course playlist
        for file_href, resource in resources.iteritems():
            if file_href not in file_hrefs:
                # Note that at this point the file object is not available. We
                # *could* fetch the corresponding file from the API, but that
                # would require one API call per file, which would be
                # prohibitive. In practice, this means that we do not have
                # access to the encoding status of files that do not belong to
                # the course folder.
                yield self.convert_resource_to_video(resource)

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
        self.safe_delete(
            self.urls.file_path(file_slug),
            message=_("Could not delete video")
        )

    def update_video_title(self, video_id, title):
        self.safe_put(
            self.urls.resource_path(video_id), {"title": title},
            message=_("Could not change video title")
        )
        return {}

    def get_upload_url(self):
        etree = parse_xml(self.safe_post(
            self.urls.upload_links_path(self.directory_slug),
            _("Could not fetch upload url")
        ))
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
        self.safe_put(
            self.urls.resource_path(video_id),
            {'visibility': visibility},
            message=_("Could not change video visibility")
        )
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
        resource = self.get_resource(video_id)
        file_slug = self.get_resource_file_slug(resource)
        self.safe_post(
            self.urls.subtitles_path(file_slug),
            files={'subtitle': file_object},
            params={'language': language},
            message=_("Could not upload subtitle")
        )

    def delete_video_subtitle(self, video_id, subtitle_id):
        resource = self.get_resource(video_id)
        file_slug = self.get_resource_file_slug(resource)
        self.safe_delete(
            self.urls.subtitle_path(file_slug, subtitle_id),
            message=_("Could not delete subtitle")
        )

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


class SelfExpiringLock(object):
    """
    Lock based on a cache value. The lock will expire on exit.

    Usage:
        with SelfExpiringLock("mykey"):
            # non thread-safe code
            ...
    """

    def __init__(self, name, timeout=None):
        self.name = name
        self.timeout = timeout
        self.cache = get_cache('default')

    def __enter__(self):
        while self.cache.get(self.name):
            pass
        self.cache.set(self.name, 1, timeout=self.timeout)

    def __exit__(self, _type, value, traceback):
        self.cache.delete(self.name)


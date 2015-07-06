# -*- coding: utf-8 -*-
from functools import wraps

from django.shortcuts import Http404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from edxmako.shortcuts import render_to_response
from util.json_request import JsonResponse

from videoproviders.api import dm
from videoproviders.forms import SubtitleForm, ThumbnailForm
from ..utils.views import has_write_access_to_course


def catch_missing_credentials_error(view_func):
    """View decorator to catch MissingCredentials exceptions."""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except dm.MissingCredentials as e:
            return json_error_response(
                _("Missing credentials:"),
                _("""There is no video storage credentials defined for this account. """
                  """Please get in touch with your administrator or support team to """
                  """setup the credentials for university '{}'""").format(e.message)
            )
    return wrapped

@has_write_access_to_course
@catch_missing_credentials_error
def home(request, course_key_string):
    course_module = dm.Client.get_course_module(course_key_string)
    return render_to_response('videoupload/index.html', {
        "context_course": course_module,
    })

@has_write_access_to_course
@catch_missing_credentials_error
def get_videos(request, course_key_string):
    dm_client = dm.Client(course_key_string)

    # Get list of uploaded videos
    try:
        videos = dm_client.get_videos()
        return JsonResponse({
            "videos": videos
        })
    except dm.ClientError as e:
        return json_error_response(_("Could not fetch video list:"), e.message)

@has_write_access_to_course
@catch_missing_credentials_error
def video(request, course_key_string, video_id):
    dm_client = dm.Client(course_key_string)
    if method_is(request, 'GET'):
        return get_video(request, dm_client, video_id)
    elif method_is(request, 'DELETE'):
        return delete_video(request, dm_client, video_id)
    elif method_is(request, 'POST'):
        return update_video(request, dm_client, video_id)
    else:
        raise Http404()

def method_is(request, method):
    """
    Detect the method employed to fire this request by combining both the
    request.method attribute and the X-HTTP-Method-Override POST header. This
    header is employed by Backbone because we use the emulateHTTP option.
    """
    method = method.upper()
    request_method = request.method.upper()
    overridden_method = request.POST.get("X-HTTP-Method-Override", "").upper()
    return request_method == method or (
        method != 'POST' and request_method == 'POST' and overridden_method == method
    )

def get_video(request, dm_client, video_id):
    try:
        return JsonResponse(dm_client.get_video(video_id))
    except dm.ClientError as e:
        return json_error_response(_("Could not fetch video:"), e.message)

def delete_video(request, dm_client, video_id):
    try:
        return JsonResponse(dm_client.delete_video(video_id))
    except dm.ClientError as e:
        return json_error_response(_("Could not delete video:"), e.message)

def update_video(request, dm_client, video_id):
    # Currently, we may only change the video title
    title = request.POST.get("title")
    try:
        return JsonResponse(dm_client.update_video(video_id, title=title))
    except dm.ClientError as e:
        return json_error_response(_("Could not change video title:"), e.message)

@has_write_access_to_course
@catch_missing_credentials_error
def file_upload(request, course_key_string):
    dm_client = dm.Client(course_key_string)
    try:
        return JsonResponse(dm_client.get_upload_url())
    except dm.ClientError as e:
        return json_error_response(_("Could not fetch upload url:"), e.message)

@require_POST
@has_write_access_to_course
@catch_missing_credentials_error
def create_video(request, course_key_string):
    url = request.POST.get("url")
    title = request.POST.get("title")
    if not url:
        raise Http404()

    dm_client = dm.Client(course_key_string)
    try:
        return JsonResponse(dm_client.create_video(url, title=title))
    except dm.ClientError as e:
        return json_error_response(_("Could not create video:"), e.message)

@require_POST
@has_write_access_to_course
@catch_missing_credentials_error
def publish_video(request, course_key_string):
    video_id = request.POST.get("video_id")
    title = request.POST.get("title")
    if not video_id or not title:
        raise Http404()

    dm_client = dm.Client(course_key_string)
    try:
        return JsonResponse(
            # Set channel and tags while we are at it
            dm_client.update_video(
                video_id,
                published=True,
                title=title,
                channel="school",
                tags=[u"France Université Numérique"]
            )
        )
    except dm.ClientError as e:
        return json_error_response(_("Could not publish video:"), e.message)

@require_POST
@has_write_access_to_course
@catch_missing_credentials_error
def unpublish_video(request, course_key_string):
    video_id = request.POST.get("video_id")
    if not video_id:
        raise Http404()

    dm_client = dm.Client(course_key_string)
    try:
        return JsonResponse(
            dm_client.update_video(
                video_id,
                published=False,
            )
        )
    except dm.ClientError as e:
        return json_error_response(_("Could not unpublish video:"), e.message)

@has_write_access_to_course
@catch_missing_credentials_error
def video_subtitles(request, course_key_string, video_id):
    """GET all video subtitles or POST a new subtitle"""
    dm_client = dm.Client(course_key_string)
    if method_is(request, 'GET'):
        try:
            return JsonResponse(dm_client.get_video_subtitles(video_id))
        except dm.ClientError as e:
            return json_error_response(_("Could not fetch video subtitles:"), e.message)
    elif method_is(request, 'POST'):
        form = SubtitleForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                return JsonResponse(upload_subtitles(
                    dm_client,
                    form.cleaned_data["video_id"],
                    form.cleaned_data["uploaded_file"],
                    form.cleaned_data["language"],
                ))
            except dm.ClientError as e:
                return json_error_response(_("Could not add subtitles:"), e.message)
        else:
            return json_error_response(_("Could not upload subtitles"), form.formatted_errors())
    else:
        raise Http404()

@has_write_access_to_course
@catch_missing_credentials_error
def video_subtitle(request, course_key_string, video_id, subtitle_id):
    """GET or DELETE a specific video subtitle"""
    dm_client = dm.Client(course_key_string)
    if method_is(request, 'GET'):
        try:
            return JsonResponse(dm_client.get_video_subtitle(video_id, subtitle_id))
        except dm.ClientError as e:
            return json_error_response(_("Could not fetch subtitle:"), e.message)
    elif method_is(request, 'DELETE'):
        try:
            return JsonResponse(dm_client.delete_video_subtitle(video_id, subtitle_id))
        except dm.ClientError as e:
            return json_error_response(_("Could not delete subtitle:"), e.message)
    else:
        raise Http404()

def upload_subtitles(dm_client, video_id, uploaded_file, language):
    subtitle_url = dm_client.upload_file(uploaded_file)
    return dm_client.post(
        '/video/{}/subtitles'.format(video_id),
        {'url': subtitle_url, 'language': language, 'format': 'SRT'}
    )

@has_write_access_to_course
@catch_missing_credentials_error
@require_POST
def video_update_thumbnail(request, course_key_string, video_id):
    form = ThumbnailForm(request.POST, request.FILES)
    if form.is_valid():
        dm_client = dm.Client(course_key_string)
        try:
            return JsonResponse(upload_thumbnail(
                dm_client,
                form.cleaned_data["video_id"],
                form.cleaned_data["uploaded_file"],
            ))
        except dm.ClientError as e:
            return json_error_response(_("Could not add thumbnail:"), e.message)
    else:
        return json_error_response(_("Could not upload thumbnail"), form.formatted_errors())

def upload_thumbnail(dm_client, video_id, uploaded_file):
    thumbnail_url = dm_client.upload_file(uploaded_file)
    return dm_client.update_video(video_id, thumbnail_url=thumbnail_url)

def json_error_response(title, message):
    return JsonResponse({
        "error": title + " " + message
    })


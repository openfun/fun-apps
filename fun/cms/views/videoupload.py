# -*- coding: utf-8 -*-
from functools import wraps
import json

from django.shortcuts import Http404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from edxmako.shortcuts import render_to_response
from util.json_request import JsonResponse

from fun.utils import get_course
from videoproviders.api import get_client, MissingCredentials, ClientError
from videoproviders.forms import SubtitleForm, ThumbnailForm
from ..utils.views import has_write_access_to_course


def catch_missing_credentials_error(view_func):
    """View decorator to catch MissingCredentials exceptions."""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except MissingCredentials as e:
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
    course_module = get_course(course_key_string)
    return render_to_response('videoupload/index.html', {
        "context_course": course_module,
    })

@has_write_access_to_course
@catch_missing_credentials_error
def get_videos(request, course_key_string):
    api_client = get_client(course_key_string)

    # Get list of uploaded videos
    try:
        videos = api_client.get_videos()
        return JsonResponse({
            "videos": videos
        })
    except ClientError as e:
        return json_error_response(_("Could not fetch video list:"), e.message)

@has_write_access_to_course
@catch_missing_credentials_error
def video(request, course_key_string, video_id):
    api_client = get_client(course_key_string)
    if method_is(request, 'GET'):
        return get_video(request, api_client, video_id)
    elif method_is(request, 'DELETE'):
        return delete_video(request, api_client, video_id)
    elif method_is(request, 'POST'):
        return update_video(request, api_client, video_id)
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

def get_video(request, api_client, video_id):
    try:
        return JsonResponse(api_client.get_video(video_id))
    except ClientError as e:
        return json_error_response(_("Could not fetch video:"), e.message)

def delete_video(request, api_client, video_id):
    try:
        api_client.delete_video(video_id)
        return JsonResponse({})
    except ClientError as e:
        return json_error_response(_("Could not delete video:"), e.message)

def update_video(request, api_client, video_id):
    # Currently, we may only change the video title
    title = request.POST.get("title")
    try:
        return JsonResponse(api_client.update_video_title(video_id, title))
    except ClientError as e:
        return json_error_response(_("Could not change video title:"), e.message)

@has_write_access_to_course
@catch_missing_credentials_error
def file_upload(request, course_key_string):
    api_client = get_client(course_key_string)
    try:
        return JsonResponse(api_client.get_upload_url())
    except ClientError as e:
        return json_error_response(_("Could not fetch upload url:"), e.message)

@require_POST
@has_write_access_to_course
@catch_missing_credentials_error
def create_video(request, course_key_string):
    payload = request.POST.get("payload")
    title = request.POST.get("title")
    if not payload:
        raise Http404()
    try:
        payload = json.loads(payload)
    except ValueError:
        raise Http404()

    api_client = get_client(course_key_string)
    try:
        return JsonResponse(api_client.create_video(payload, title=title))
    except ClientError as e:
        return json_error_response(_("Could not create video:"), e.message)

@require_POST
@has_write_access_to_course
@catch_missing_credentials_error
def publish_video(request, course_key_string):
    video_id = request.POST.get("video_id")
    title = request.POST.get("title")
    if not video_id or not title:
        raise Http404()

    api_client = get_client(course_key_string)
    try:
        return JsonResponse(api_client.publish_video(video_id))
    except ClientError as e:
        return json_error_response(_("Could not publish video:"), e.message)

@require_POST
@has_write_access_to_course
@catch_missing_credentials_error
def unpublish_video(request, course_key_string):
    video_id = request.POST.get("video_id")
    if not video_id:
        raise Http404()

    api_client = get_client(course_key_string)
    try:
        return JsonResponse(api_client.unpublish_video(video_id))
    except ClientError as e:
        return json_error_response(_("Could not unpublish video:"), e.message)

@has_write_access_to_course
@catch_missing_credentials_error
def video_subtitles(request, course_key_string, video_id):
    """GET all video subtitles or POST a new subtitle"""
    api_client = get_client(course_key_string)
    if method_is(request, 'GET'):
        try:
            return JsonResponse(api_client.get_video_subtitles(video_id))
        except ClientError as e:
            return json_error_response(_("Could not fetch video subtitles:"), e.message)
    elif method_is(request, 'POST'):
        form = SubtitleForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                api_client.upload_subtitle(
                    form.cleaned_data["video_id"],
                    form.cleaned_data["uploaded_file"],
                    form.cleaned_data["language"],
                )
                return JsonResponse({})
            except ClientError as e:
                return json_error_response(_("Could not add subtitles:"), e.message)
        else:
            return json_error_response(_("Could not upload subtitles"), form.formatted_errors())
    else:
        raise Http404()

@has_write_access_to_course
@catch_missing_credentials_error
def video_subtitle(request, course_key_string, video_id, subtitle_id):
    """GET or DELETE a specific video subtitle"""
    api_client = get_client(course_key_string)
    if method_is(request, 'DELETE'):
        try:
            api_client.delete_video_subtitle(video_id, subtitle_id)
            return JsonResponse({})
        except ClientError as e:
            return json_error_response(_("Could not delete subtitle:"), e.message)
    else:
        raise Http404()

@has_write_access_to_course
@catch_missing_credentials_error
@require_POST
def video_update_thumbnail(request, course_key_string, video_id):
    form = ThumbnailForm(request.POST, request.FILES)
    if form.is_valid():
        api_client = get_client(course_key_string)
        try:
            return JsonResponse(api_client.upload_thumbnail(
                form.cleaned_data["video_id"],
                form.cleaned_data["uploaded_file"],
            ))
        except ClientError as e:
            return json_error_response(_("Could not add thumbnail:"), e.message)
    else:
        return json_error_response(_("Could not upload thumbnail"), form.formatted_errors())

def json_error_response(title, message):
    return JsonResponse({
        "error": title + " " + message
    })

